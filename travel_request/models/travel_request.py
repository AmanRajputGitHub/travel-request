# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class TravelType(models.Model):
    _name = "travel.type"

    name = fields.Char()


class TravelRequest(models.Model):
    _name = "travel.request"

    name = fields.Char()
    employee_id = fields.Many2one("hr.employee")
    travel_start_date = fields.Date()
    travel_end_date = fields.Date()
    travel_days = fields.Integer(compute="_calculate_travel_days")
    # travel_type = fields.Selection([('air', "Air"), ('train', "Train"), ('road', "Road")])
    department_id = fields.Many2one("hr.department", "Department")
    travel_type_id = fields.Many2one("travel.type")
    added_by_id = fields.Many2one("hr.employee", "Added By")
    purpose_of_visit = fields.Text()
    approved_by_id = fields.Many2one("hr.employee", "Approved By")
    advance_amount = fields.Float()
    currency_id = fields.Many2one("res.currency", "Currency")
    project_id = fields.Many2one("project.project", "Project")
    state = fields.Selection([('draft', "Draft"), ('submitted', "Submitted"), ('approve', "Approved"), ('reject', "Rejected")], default="draft")
    proposed_travel_detail_ids = fields.One2many('proposed.travel.detail', 'travel_request_id')
    logistic_requirement_ids = fields.One2many('logistic.requirement', 'travel_request_id')
    travel_expense_estimated_ids = fields.One2many('travel.expense.estimated', 'travel_request_id')
    reporting_manager_id = fields.Many2one('hr.employee', string="Reporting Manager")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            rec.reporting_manager_id = rec.employee_id.parent_id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('travel.request') or _('New')
        result = super(TravelRequest, self).create(vals)

        for request in result:
            if request.reporting_manager_id.work_email:
                template = request.env.ref('travel_request.new_travel_request_email_template')
                template_values = {
                    'email_from': request.employee_id.work_email,
                    'email_to': request.reporting_manager_id.work_email or 'safe',
                    'auto_delete': True,
                    'partner_to': False,
                    'scheduled_date': False,
                }
                template.write(template_values)
                template.send_mail(request.id, notif_layout='mail.mail_notification_light')
        return result


    @api.depends('travel_start_date', 'travel_end_date')
    def _calculate_travel_days(self):
        for travel in self:
            if travel.travel_start_date and travel.travel_end_date:
                travel.travel_days = (travel.travel_end_date - travel.travel_start_date).days
            else:
                travel.travel_days = 0

    def action_submit(self):
        for travel in self:
            travel.state = 'submitted'

    def action_approve(self):
        for travel in self:
            travel.state = 'approve'

    def action_reject(self):
        for travel in self:
            travel.state = 'reject'


class ProposedTravelDetail(models.Model):
    _name = "proposed.travel.detail"


    date_of_travel = fields.Date()
    am_pm = fields.Selection([('am', "AM"), ('pm', "PM")])
    time = fields.Float()
    travel_from = fields.Char("From")
    travel_to = fields.Char("To")
    travel_type = fields.Selection([('air', "Air"), ('train', "Train"), ('bus', "Bus"), ('car', "Car")])
    admin_support_required = fields.Selection([('yes', "Yes"), ('no', "No")])
    travel_request_id = fields.Many2one('travel.request')


class LogisticRequirement(models.Model):
    _name = "logistic.requirement"


    head = fields.Selection([('drop', "Drop"), ('pickup', "Pickup"),('local_travel', "Local Travel"), ('other', "Other")])
    l_date = fields.Date("Date")
    city = fields.Char("City")
    admin_support_required = fields.Selection([('yes', "Yes"), ('no', "No")])
    remark = fields.Char("Remarks")
    travel_request_id = fields.Many2one('travel.request')


class TravelExpenseEstimated(models.Model):
    _name = "travel.expense.estimated"


    # head = fields.Selection([('drop', "Drop"), ('pickup', "Pickup"),('local_travel', "Local Travel"), ('other', "Other")])
    head_id = fields.Many2one("head.name")
    no_of_days = fields.Integer("No. of days")
    approx_rate_amount = fields.Float("Approx. Rate: amount")
    approx_rate_gbp = fields.Float("Approx. rate in GBP / USD Eur Total")
    total_amount = fields.Float("Total Amount", compute="_get_total_amount")
    travel_request_id = fields.Many2one("travel.request")
    traven_expense_id = fields.Many2one("travel.expenses.detail")

    date_of_expense = fields.Date()
    bill_no = fields.Char()
    particulars = fields.Char()
    upload_receipt = fields.Binary(attachment=True, string="Upload Receipt")
    amount_over = fields.Float()
    remark = fields.Char()    

    @api.depends('approx_rate_amount', 'no_of_days')
    def _get_total_amount(self):
        for travel_expense in self:
            travel_expense.total_amount = travel_expense.no_of_days * travel_expense.approx_rate_amount


class HeadName(models.Model):
    _name = "head.name"

    name = fields.Char()
    head_type = fields.Selection([('logistic', "Logistic"), ('travelling', "Travelling")])
