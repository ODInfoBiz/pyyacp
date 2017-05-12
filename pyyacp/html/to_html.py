
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

PATH = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates'))
)



def to_html(table, cnt, dir):
    m_order=['data_type','data_class','patterns',
             'stats_num_rows','stats_distinct','stats_empty',
             'stats_min_len','stats_mean_len','stats_max_len',
             'stats_constancy','stats_uniqueness','stats_top_value',
             'c_dist_dist','benford_is','benford_chi','benford_dist']
    output = os.path.join('.', "../html/{}.html".format(cnt))
    with open(output, "w") as f:
        template = env.get_template('profile.jinja')
        f.write(template.render(
            basic=table.basic(),
            columnIDs=table.columnIDs,
            tmeta=table.meta,
            m_order=m_order,
            comments=table.comments,
            data=table.data.head(5).to_html(classes='ui celled table'),
            meta=table.describe_colmeta().to_dict(orient='index')#table.describe_colmeta().to_html(classes='ui celled table')
        ).encode('utf-8'))


