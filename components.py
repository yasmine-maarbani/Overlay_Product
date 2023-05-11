import streamlit as st


def form_input(key: int, select_label: str, select_options: list, text_label: str, text_placeholder: str,
               text_options: list, prompt: str):
    """
    :param key: unique key for each form input
    :param select_label: label for selectbox
    :param select_options: options for selectbox
    :param text_label: label for text input
    :param text_placeholder: placeholder for text input
    :param text_options: options for text input
    :param prompt: prompt string
    :return: prompt
    """
    select = st.selectbox(select_label, select_options)
    if select == "custom":
        text = st.text_input(text_label,
                             label_visibility='collapsed',
                             placeholder=text_placeholder,
                             max_chars=40)
        weight = st.number_input(label="Strength", min_value=1.0, max_value=2.0, step=0.1, key=key)
        weight = round(weight, 2)
        prompt = f"{prompt}, ({text}: {weight})" if weight != 1.0 else f"{prompt}, ({text})"
    elif select == "None":
        pass
    else:
        text = st.selectbox(text_label,
                            text_options,
                            label_visibility='collapsed')
        weight = st.number_input(label="Strength", min_value=1.0, max_value=2.0, step=0.1, key=key)
        weight = round(weight, 2)
        prompt = f"{prompt} , ({select} {text}: {weight})" if weight != 1.0 else f"{prompt} , {select} {text}"
    st.divider()

    return prompt
