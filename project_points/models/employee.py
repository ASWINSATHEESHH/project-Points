from odoo import models,fields,api,_

class Employee(models.Model):
    _inherit = 'hr.employee'

    points = fields.Float('Points')

    def btn_project_point(self):
        pass