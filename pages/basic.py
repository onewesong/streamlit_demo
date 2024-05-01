from modules import *

tab_text, tab_data, tab_media, tab_widgets, tab_notify, tab_status = st.tabs(["Text", "Data", "Media", "Widgets", "Notifications", "Status"])

with tab_text:
    with st.echo():
        st.text("This is tab 1", help="help text")
        st.markdown('_Markdown_')
        st.caption('Balloons. Hundreds of them...')
        st.latex(r''' e^{i\pi} + 1 = 0 ''')
        st.write('Most objects') # df, err, func, keras!
        st.write(['st', 'is <', 3]) # see *
        st.title('My title')
        st.header('My header')
        st.subheader('My sub')
        st.code('for i in range(8): foo()')

with tab_data:
    with st.echo():
        st.dataframe(dataframe)
    with st.echo():
        st.table(dataframe.iloc[0:2])
    with st.echo():
        st.json({'foo':'bar','fu':'ba'})
    with st.echo():
        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", "70 °F", "1.2 °F")
        col2.metric("Wind", "9 mph", "-8%")
        col3.metric("Humidity", "86%", "4%")

with tab_media:
    with st.echo():
        st.image("./assets/👑.png", width=100)
        st.audio('https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_30mb.mp4')
        st.video('https://sample-videos.com/video321/mp4/480/big_buck_bunny_480p_30mb.mp4')

with tab_widgets:
    with st.echo():
        if 'hit_count' not in st.session_state:
            st.session_state.hit_count = 0
        if st.button("Hit me"):
            st.session_state.hit_count += 1
            st.metric("Hit_count", st.session_state.hit_count, delta=1)
    with st.echo():
        st.checkbox("Check me out", key="checked")
        st.text(f"IsChecked: {st.session_state.checked}")
    with st.echo():
        st.radio("Radio", [1,2,3,4])
    with st.echo():
        st.selectbox("Select", [1,2,3,4])
        st.multiselect('Multiselect', [1,2,3])
    with st.echo():
        st.slider("Slide me", min_value=0, max_value=10)
        st.slider("Slide me", min_value=0.0, max_value=10.0, step=0.1)
    with st.echo():
        if st.text_input("Your name", key="your_name"):
            st.text(f"Hello {st.session_state.your_name}")
    with st.echo():
        st.number_input("Enter a number", key="number")
        st.text(f"number is: {st.session_state.number}")
    with st.echo():
        st.color_picker("Pick a color", key="color")
        st.text(f"color is: {st.session_state.color}")
    # with st.echo():
    #     st.camera_input("一二三,茄子!")
    with st.echo():
        if file := st.file_uploader('File uploader'):
            st.write(file)
            st.text_area("File contents", file.getvalue())
            st.download_button('Download your file', file, file.name)

with tab_notify:
    with st.echo():
        st.balloons()
        st.snow()
        st.toast('toast message1')
        st.toast('toast message2')
        st.error('Error message')
        st.warning('Warning message')
        st.info('Info message')
        st.success('Success message')
        e = Exception('This is a test exception')
        st.exception(e)


with tab_status:
    with st.echo():
        with st.spinner('Wait for it...'):
            time.sleep(5)
        st.success('Success message')
        st.error('Error message')
        st.warning('Warning message')
        st.info('Info message')
        st.stop()
        st.write('This line will not be executed.')