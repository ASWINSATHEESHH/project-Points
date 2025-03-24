from odoo import models,fields,api,_

class Employee(models.Model):
    _inherit = 'hr.employee'

    points = fields.Float('Points')

    def btn_project_point(self):
        return {
            'name': 'My Projects',
            'type': 'ir.actions.act_window',
            'res_model': 'project.points',
            'view_mode': 'tree,form',
            'domain': [('users_ids', 'in', self.user_id.id)],
        }