#  Copyright (c) 2023.
#
from reactpy import component, html


@component
def hello_world(recipient: str):
    return html.h1(f"Hello {recipient}!")