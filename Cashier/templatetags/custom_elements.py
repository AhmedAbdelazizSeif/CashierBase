#  Copyright (c) 2024.
#
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def floating_label_input(label, name, span_width='', custom_function=None, custom_function_args=None):
    """Renders a floating label input element."""
    div_class = 'relative'
    if span_width:
        div_class += f" sm:col-span-{span_width}" if "full" not in span_width else f" col-span-full"

    input_class = 'block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer'
    label_class = 'absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1'
    if not custom_function:
        element = f"""
        <div class="{div_class}">
            <input type="text" name="{name}" id="{name}" class="{input_class}" placeholder=" " />
            <label for="{name}" class="{label_class}">{label}</label>
        </div>
        """
    else:
        element = f"""
        <div class="{div_class}">
            <input type="text" name="{name}" id="{name}" class="{input_class}" placeholder=" " {custom_function}="{custom_function_args}" />
            <label for="{name}" class="{label_class}">{label}</label>
        </div>
        """
    return mark_safe(element)
