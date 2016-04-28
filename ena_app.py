from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
from dateutil.parser import parse
import datetime

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        result = request.form.get('date')
        if result is not None:
            return redirect(url_for('date_page', date=result))
    else:
        return render_template('index.html')
    # return "<h1 style='color:blue'>Hello World!!</h1>"

@app.route('/date/<date>')
def date_page(date):

    date_as_dt = parse(date)
    dt_fmt = '%Y-%m-%d'

    date_as_string = date_as_dt.strftime(dt_fmt)

    next_date = (date_as_dt + datetime.timedelta(days=1)).strftime(dt_fmt)
    prev_date = (date_as_dt - datetime.timedelta(days=1)).strftime(dt_fmt)

    aer_figure = 'https://s3-us-west-2.amazonaws.com/arm-ena-data/figures/{}_aerosol.png'.format(date_as_string)
    met_figure = 'https://s3-us-west-2.amazonaws.com/arm-ena-data/figures/{}_met.png'.format(date_as_string)
    rose_figure = 'https://s3-us-west-2.amazonaws.com/arm-ena-data/figures/{}_windrose.png'.format(date_as_string)
    #aer_figure = url_for('static', filename='figures/{}_aerosol.png'.format(date_as_string))
    #met_figure = url_for('static', filename='figures/{}_met.png'.format(date_as_string))

    args = {'aer': aer_figure,
            'met': met_figure,
            'rose': rose_figure,
            'date': date_as_string,
            'next': next_date,
            'prev': prev_date}

    return render_template('date_page.html', **args)

@app.route('/interesting_cases')
def cases():
    table = pd.read_csv('https://docs.google.com/spreadsheets/d/' +
                    '1j-yL-SXwPXMxEzhrx7plkggPYJ6WlHD3EM7gVte7Ba8/' +
                    'pub?gid=1851660263&single=true&output=csv',
                    names=['tstamp', 'case_date', 'description', 'category'],
                    parse_dates=[0,],
                    header=0)
    table['case_dt'] = table['case_date'].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y'))
    new_table = table.set_index('case_dt')[['description', 'category']].sort_index()

    d = new_table.groupby('category').apply(lambda x: x.to_dict()).to_dict()

    return render_template('interesting_cases.html', cases=d)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
