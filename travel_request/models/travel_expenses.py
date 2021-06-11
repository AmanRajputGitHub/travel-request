# -*- coding: utf-8 -*-


from odoo import models, fields, api


class TravelExpensesDetail(models.Model):
    _name = "travel.expenses.detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Travel Expense"
    _order = 'name, id desc'
    _rec_name = 'travel_id'

    name = fields.Char()
    employee_id = fields.Many2one("hr.employee", "Employee Name")
    travel_id = fields.Many2one("travel.request", "Travel ID")
    currency_id = fields.Many2one("res.currency", "Currency")
    purpose_of_visit = fields.Char()
    advance_taken = fields.Float()
    period_from = fields.Date()
    added_by = fields.Char("")
    period_to = fields.Date()
    added_time = fields.Datetime()
    modified_by_id = fields.Many2one("hr.employee", "Modified By")
    modified_time = fields.Datetime()
    project_id = fields.Many2one("project.project", "Project Name")
    state = fields.Selection([('draft', "Draft"), ('submitted', "Submitted"), ('approved', "Approved"), ('rejected', "Rejected")], default="draft")
    expense_ids = fields.One2many("travel.expense.estimated", "traven_expense_id")

    approval_send_to = fields.Many2one('hr.employee')

    @api.onchange("travel_id")
    def onchange_travel_id(self):
        if self.travel_id:
            self.period_from = self.travel_id.travel_start_date
            self.period_to = self.travel_id.travel_end_date
            self.purpose_of_visit = self.travel_id.purpose_of_visit
            self.currency_id = self.travel_id.currency_id.id
            self.advance_taken = self.travel_id.advance_amount
            self.project_id = self.travel_id.project_id.id
            self.added_by = self.travel_id.added_by_id.name
            self.employee_id = self.travel_id.employee_id.id
            self.expense_ids = self.travel_id.travel_expense_estimated_ids.ids

    def action_submit(self):
        for expense in self:
            if expense.approval_send_to.work_email:
                template = expense.env.ref('travel_request.approval_email_template')
                template_values = {
                    'email_from': expense.employee_id.work_email,
                    'email_to': expense.approval_send_to.work_email or 'safe',
                    'auto_delete': True,
                    'partner_to': False,
                    'scheduled_date': False,
                }
                template.write(template_values)
                template.send_mail(expense.id, notif_layout='mail.mail_notification_light')
            expense.state = 'submitted'

    def action_approve(self):
        for expense in self:
            expense.state = 'approved'

    def action_reject(self):
        for expense in self:
            expense.state = 'reject'


class TravelExpensesDetail(models.Model):
    _inherit = "hr.expense"

    traven_expense_id = fields.Many2one("travel.expenses.detail")