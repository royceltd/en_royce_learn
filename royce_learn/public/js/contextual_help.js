/* No modifications to ERPNext's controllers or business transactions. */
(() => {
    const types = new Set(['Company', 'User', 'Customer', 'Item', 'Sales Invoice', 'Payment Entry']);
    $(document).on('form-refresh.royce_learn', (event, frm) => {
        if (!frm || !types.has(frm.doctype)) return;
        frm.add_custom_button(__('Help with this task'), () => {
            frappe.set_route('getting-started', {doctype: frm.doctype});
        });
    });
})();
