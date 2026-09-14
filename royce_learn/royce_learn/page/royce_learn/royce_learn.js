frappe.pages['royce-learn'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({parent: wrapper, title: __('Royce Learn'), single_column: true});
    const root = $('<div class="royce-learn">').appendTo(page.main);
    let company = null;
    let currentDoctype = '';
    let requestNumber = 0;
    const call = async (method, args = {}, type = 'GET') => {
        const response = await frappe.call({method: `royce_learn.api.${method}`, args, type});
        return response.message;
    };
    const el = (tag, text, cls = '') => $(`<${tag}>`).addClass(cls).text(__(text));
    const button = (text, action, cls = 'btn-default') => el('button', text, `btn btn-sm ${cls}`)
        .attr('type', 'button').on('click', async function() {
            $(this).prop('disabled', true);
            try { await action(); } finally { $(this).prop('disabled', false); }
        });
    const progressBar = (parent, percent) => {
        const bar = $('<div class="rl-progress" role="progressbar">').attr({
            'aria-valuenow': percent, 'aria-valuemin': 0, 'aria-valuemax': 100,
            'aria-label': __('Progress')
        }).appendTo(parent);
        $('<span>').css('width', `${percent}%`).appendTo(bar);
    };
    const openGuide = async (id) => {
        const item = await call('guide', {guide_id: id});
        const dialog = new frappe.ui.Dialog({title: item.title, size: 'large', fields: [{fieldname: 'content', fieldtype: 'HTML'}],
            primary_action_label: __('Mark lesson completed'),
            primary_action: async () => {
                await call('mark_learning', {guide_id: id, status: 'Completed'}, 'POST');
                dialog.hide(); await load();
            }});
        const body = dialog.fields_dict.content.$wrapper;
        el('p', item.summary).appendTo(body);
        el('div', item.body, 'rl-guide-body').appendTo(body);
        const actions = $('<div class="rl-actions">').appendTo(body);
        if (item.doctype) button('Open ERP screen', () => {
            dialog.hide(); frappe.set_route('List', item.doctype);
        }).appendTo(actions);
        if (item.video_id) button('Load video', () => {
            // Explicit action avoids contacting YouTube until the user chooses to load it.
            $('<iframe class="rl-video">').attr({
                src: `https://www.youtube-nocookie.com/embed/${item.video_id}`,
                title: item.title, loading: 'lazy', allowfullscreen: 'allowfullscreen',
                referrerpolicy: 'strict-origin-when-cross-origin',
                sandbox: 'allow-scripts allow-same-origin allow-presentation'
            }).appendTo(body);
        }).appendTo(actions);
        if (item.updated_since_completion) el('p', 'This guide has changed since you completed it.').appendTo(body);
        dialog.show();
        await call('mark_learning', {guide_id: id, status: 'In Progress'}, 'POST');
    };
    const confirmStep = async (step, status) => {
        if (status === 'Not Applicable') {
            frappe.prompt([{fieldname: 'note', fieldtype: 'Small Text', label: __('Reason'), reqd: 1}], async values => {
                await call('confirm_setup', {company, step_id: step.id, status, note: values.note}, 'POST'); await load();
            }, __('Opening balances do not apply'));
            return;
        }
        await call('confirm_setup', {company, step_id: step.id, status}, 'POST'); await load();
    };
    const renderGuides = (target, guides) => {
        target.empty();
        if (!guides.length) {el('p', 'No guides match your search and access.').appendTo(target); return;}
        for (const guide of guides) {
            const card = $('<article class="rl-card">').appendTo(target);
            el('div', guide.category, 'rl-status').appendTo(card);
            el('h3', guide.title).appendTo(card);
            el('p', guide.summary).appendTo(card);
            el('div', `${guide.minutes || 3} min · ${guide.status}`, 'rl-status').appendTo(card);
            if (guide.updated_since_completion) el('div', 'Updated since completion', 'rl-status').appendTo(card);
            button('Read guide', () => openGuide(guide.id)).appendTo(card);
        }
    };
    const load = async () => {
        const sequence = ++requestNumber;
        const data = await call('dashboard', {company});
        if (sequence !== requestNumber) return;
        company = data.company;
        root.empty();
        el('h1', 'Learn your ERP. Get your business ready.').appendTo(root);
        el('p', 'Follow setup tasks, find help, and continue your learning.', 'rl-intro').appendTo(root);
        const companyControls = $('<div class="rl-controls">').appendTo(root);
        const select = $('<select class="form-control">').attr('aria-label', __('Company')).appendTo(companyControls);
        for (const name of data.companies) $('<option>').val(name).text(name).appendTo(select);
        select.val(company).on('change', async () => {company = select.val(); await load();});
        if (data.setup) {
            const setup = $('<section class="rl-card">').appendTo(root);
            el('h2', 'Getting Started').appendTo(setup);
            el('p', `${data.setup.completed} of ${data.setup.total} tasks complete for ${company}`).appendTo(setup);
            el('p', data.setup.progress_scope, 'rl-status').appendTo(setup);
            progressBar(setup, data.setup.percent);
            for (const step of data.setup.steps) {
                const row = $('<div class="rl-step">').appendTo(setup);
                const details = $('<div>').appendTo(row);
                el('strong', step.label).appendTo(details);
                el('div', step.status, 'rl-status').appendTo(details);
                if (step.confirmation) el('div', `Confirmed by ${step.confirmation.confirmed_by}`, 'rl-status').appendTo(details);
                const actions = $('<div class="rl-actions">').appendTo(row);
                button('Guide', () => openGuide(step.guide)).appendTo(actions);
                if (step.evidence) button('View transaction', () => frappe.set_route('Form', step.doctype, step.evidence)).appendTo(actions);
                if (step.mode === 'confirm' && data.setup.can_confirm) {
                    button(step.status === 'Pending' ? 'Confirm complete' : 'Reopen task', () => confirmStep(step, step.status === 'Pending' ? 'Complete' : 'Pending')).appendTo(actions);
                    if (step.optional && step.status === 'Pending') button('Not applicable', () => confirmStep(step, 'Not Applicable')).appendTo(actions);
                }
            }
            if (!data.setup.steps.length) el('p', 'No setup tasks are available with your current permissions.').appendTo(setup);
        } else el('p', 'Ask your administrator for access to a company to see its setup checklist.').appendTo(root);
        const paths = $('<section class="rl-section">').appendTo(root);
        el('h2', 'Your learning paths').appendTo(paths);
        el('p', `${data.learning.completed} of ${data.learning.total} lessons completed by you`).appendTo(paths);
        const pathGrid = $('<div class="rl-grid">').appendTo(paths);
        for (const path of data.paths) {
            const card = $('<article class="rl-card">').appendTo(pathGrid);
            el('h3', path.title).appendTo(card);
            el('p', path.summary).appendTo(card);
            progressBar(card, Math.round(100 * path.completed / path.total));
            const next = path.guides.find(id => data.guides.find(g => g.id === id)?.status !== 'Completed') || path.guides[0];
            button(path.completed === path.total ? 'Review lessons' : 'Continue learning', () => openGuide(next)).appendTo(card);
        }
        const library = $('<section class="rl-section">').appendTo(root);
        el('h2', 'Guide library').appendTo(library);
        const controls = $('<div class="rl-controls">').appendTo(library);
        const search = $('<input class="form-control" type="search">').attr({placeholder: __('Search guides'), 'aria-label': __('Search guides'), maxlength: 200}).appendTo(controls);
        const category = $('<select class="form-control">').attr('aria-label', __('Topic')).appendTo(controls);
        $('<option>').val('').text(__('All topics')).appendTo(category);
        for (const topic of [...new Set(data.guides.map(g => g.category))]) $('<option>').val(topic).text(topic).appendTo(category);
        if (currentDoctype) button('Show all guides', () => {currentDoctype = ''; filter();}).appendTo(controls);
        const grid = $('<div class="rl-grid">').appendTo(library);
        let searchSequence = 0;
        const filter = async () => {
            const n = ++searchSequence;
            const rows = await call('guides', {query: search.val(), category: category.val(), doctype: currentDoctype});
            if (n === searchSequence && sequence === requestNumber) renderGuides(grid, rows);
        };
        search.on('input', frappe.utils.debounce(filter, 250)); category.on('change', filter);
        if (currentDoctype) await filter(); else renderGuides(grid, data.guides);
    };
    wrapper.royce_learn_load = () => {
        currentDoctype = frappe.route_options?.doctype || '';
        frappe.route_options = null;
        return load();
    };
};
frappe.pages['royce-learn'].on_page_show = function(wrapper) {
    wrapper.royce_learn_load().catch(() => frappe.msgprint(__('Royce Learn could not load. Please try again.')));
};
