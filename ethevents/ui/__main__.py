import inspect

import IPython
import click
from IPython.utils.coloransi import TermColors
from elasticsearch import Elasticsearch

from ethevents import App
from ethevents.client.proxy import run_proxy
from ethevents.ui.account_ui import AccountUI
import ethevents.examples.queries
import ethevents.examples.plots


class UI(AccountUI):
    def __init__(self, app: App):
        AccountUI.__init__(self, app)


def help():
    print(
        'Welcome to the eth.events interactive shell.\n'
        'Use {b}es{n} to perform Elasticsearch queries.\n'
        'Use {b}ee{n} to manage your µRaiden channel and account.\n'
        'You can find sample queries in the {b}queries{n} and {b}plots{n} modules.'.format(
            b=TermColors.Blue,
            n=TermColors.Normal
        )
    )


@click.option(
    '--limits/--no-limits',
    default=True
)
@click.command()
def main(limits: bool):
    proxy, proxy_greenlet, app = run_proxy(
        endpoint_url='https://api.eth.events',
        ignore_security_limits=not limits
    )

    ui = UI(app)
    ui_methods = {
        'ee_{}'.format(method_name): method
        for method_name, method in inspect.getmembers(ui, predicate=inspect.ismethod)
        if '__' not in method_name[:2]
    }
    if proxy is not None:
        ee_queries = ethevents.examples.queries
        ee_plots = ethevents.examples.plots
        ee_es = Elasticsearch(['http://localhost:5478'], timeout=30)
        IPython.start_ipython(
            user_ns=dict(
                ee_queries=ee_queries,
                ee_plots=ee_plots,
                ee_es=ee_es,
                es=ee_es,
                queries=ee_queries,
                plots=ee_plots,
                **ui_methods,
                help=help
            ),
            argv=[],
        )

        proxy.stop()
        proxy_greenlet.join(timeout=5)


def entrypoint():
    import logging
    logging.basicConfig(level=logging.INFO, filename='ethevents.log')
    main()


if __name__ == '__main__':
    entrypoint()
