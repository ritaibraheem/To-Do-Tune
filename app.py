from datetime import datetime, date
# from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
# from htbuilder.units import percent, px
# from htbuilder.funcs import rgba, rgb
import streamlit as st
import pandas as pd 
from db_funcs import *
from PIL import Image
import plotly.express as px 

# def image(src_as_string, **style):
#     return img(src=src_as_string, style=styles(**style))


# def link(link, text, **style):
#     return a(_href=link, _target="_blank", style=styles(**style))(text)


# def layout(*args):

#     style = """
#     <style>
#       # MainMenu {visibility: hidden;}
#       footer {visibility: hidden;}
#      .stApp { bottom: 105px; }
#     </style>
#     """

#     style_div = styles(
#         position="fixed",
#         left=0,
#         bottom=0,
#         margin=px(0, 0, 0, 0),
#         width=percent(100),
#         color="black",
#         text_align="center",
#         height="auto",
#         opacity=1
#     )

#     style_hr = styles(
#         display="block",
#         margin=px(8, 8, "auto", "auto"),
#         border_style="inset",
#         border_width=px(2)
#     )

#     body = p()
#     foot = div(
#         style=style_div
#     )(
#         hr(
#             style=style_hr
#         ),
#         body
#     )

#     st.markdown(style, unsafe_allow_html=True)

#     for arg in args:
#         if isinstance(arg, str):
#             body(arg)

#         elif isinstance(arg, HtmlElement):
#             body(arg)

#     st.markdown(str(foot), unsafe_allow_html=True)


# def footer():
#     myargs = ["Made with ❤️ by Bella & Rita"]
#     layout(*myargs)

# *******************************************
# App Components
# *******************************************

def color_df(val):
	if val == "Done":
		color = "green"
	elif val == "In-Progress":
		color = "orange"
	else:
		color = "red"  

	return f'background-color: {color}'

st.set_page_config(
    page_title="ToDo Tune",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# top_image = Image.open('static/banner_top.png')
bottom_image = Image.open('static/banner_bottom.png')
# main_image = Image.open('static/main_banner.png')

# st.image(main_image,use_column_width='always')
st.title("📄 ToDo Tune")

# st.sidebar.image(top_image,use_column_width='auto')
choice = st.sidebar.selectbox("Menu", ["My Day 🎯","Create Task ✅","Update Task 🖊️","Delete Task ❌", "View Tasks' Status 👨‍💻"])
st.sidebar.image(bottom_image,use_column_width='auto')
create_table()

if choice == "My Day 🎯":
	st.subheader("My Day 🎯")

	col_large1,col_large2 = st.columns(2,gap='medium')
	
	with col_large1:
		st.text('How do you feel today?')
		feeling = None

		col1,col2,col3,col4,col5 = st.columns(5,gap='small')
		with col1:
			if st.button('😁'): #super happy
				feeling = 5
		with col2:
			if st.button('🙂'): #happy
				feeling = 4	
		with col3:
			if st.button('😐'): #neutral
				feeling = 3
		with col4:
			if st.button('🙁'): #sad
				feeling = 2
		with col5:
			if st.button('😭'): #super sad
				feeling = 1

		avg_mood_int=feeling

	with col_large2:
		avg_sleep_hours_int = st.slider('How many hours did you sleep at night?', 0.0, 24.0, 7.0)
		st.write(avg_sleep_hours_int, ' hours.')	

	result = get_today_tasks(date.today())
	# st.write(result)
	result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'deadline_met'])
	clean_df1= result_df[['title', 'tag', 'task_status', 'deadline_date']]

	with st.expander("View Today's Tasks 📝"):
		# result = view_all_data()
		# # st.write(result)
		# result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'deadline_met'])
		# clean_df= result_df[['title', 'task_status', 'deadline']]
		# clean_df['deadline'] = pd.to_datetime(clean_df['deadline'])
		# clean_df['deadline']= clean_df['deadline'].dt.date
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))






if choice == "Create Task ✅":
	st.subheader("Add New Task")
	col1,col2 = st.columns(2)

	with col1:
		# task = st.text_area("Task To Do")
		title = st.text_input("Title")
		about = st.text_area("Description")
		

	with col2:
		tag = st.selectbox("Category",["home", "bureaucracy", "studies", "work", "exercise", "fun", "health"])
		deadline_date = st.date_input("Due Date")
		deadline = datetime.combine(deadline_date, datetime.max.time())
		time_estimation = st.number_input(label="Estimated Time (hours)", min_value=0,)
		task_status = st.selectbox("Status",["To-Do","In-Progress"])

	if task_status == "In-Progress":
			start_time=datetime.now()
	else: start_time=None

	if task_status == "Done":
			end_time=datetime.now()
			if deadline < end_time:
				deadline_met = False 
			else: deadline_met = True
	else:
		end_time=None
		deadline_met = None

	if st.button("Add Task"):
		add_row(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, deadline_met)
		st.success("Added Task \"{}\" ✅".format(title))
		st.balloons()

elif choice == "Update Task 🖊️":
	st.subheader("Edit Items")
	with st.expander("Current Data"):
		result = view_all_data()
		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

	list_of_tasks = [i[0] for i in view_all_task_names()]
	selected_task = st.selectbox("Task",list_of_tasks)
	task_result = get_task(selected_task)

	if task_result:
		task = task_result[0][0]
		task_status = task_result[0][1]
		task_due_date = task_result[0][2]

		col1,col2 = st.columns(2)

		with col1:
			new_task = st.text_area("Task To Do",task)

		with col2:
			new_task_status = st.selectbox(task_status,["To-Do","In-Progress","Done"])
			new_task_due_date = st.date_input(task_due_date)

		if st.button("Update Task 🖊️"):
			edit_task_data(new_task,new_task_status,new_task_due_date,task,task_status,task_due_date)
			st.success("Updated Task \"{}\" ✅".format(task,new_task))

		with st.expander("View Updated Data 💫"):
			result = view_all_data()
			# st.write(result)
			clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
			st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

elif choice == "Delete Task ❌":
	st.subheader("Delete")
	with st.expander("View Data"):
		result = view_all_data()
		# st.write(result)
		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

	unique_list = [i[0] for i in view_all_task_names()]
	delete_by_task_name =  st.selectbox("Select Task",unique_list)
	if st.button("Delete ❌"):
		delete_data(delete_by_task_name)
		st.warning("Deleted Task \"{}\" ✅".format(delete_by_task_name))

	with st.expander("View Updated Data 💫"):
		result = view_all_data()
		# st.write(result)
		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

elif choice == "View Tasks' Status 👨‍💻":
	result = view_all_data()
	# st.write(result)
	result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'deadline_met'])
	# clean_df= result_df[['title', 'task_status', 'deadline']] 
	# clean_df['deadline'] = pd.to_datetime(clean_df['deadline'])
	# clean_df['deadline']= clean_df['deadline'].dt.date
	clean_df= result_df[['title', 'task_status', 'deadline_date']] 

	task_df = clean_df['task_status'].value_counts().to_frame()
	task_df = task_df.reset_index()

	col1,col2 = st.columns(2)
	with col1:
		st.dataframe(task_df)
	with col2:
		p1 = px.pie(task_df,names='task_status',values='count', color='task_status', color_discrete_map={'To-Do':'red', 'Done':'green', 'In-Progress':'orange'})
		st.plotly_chart(p1,use_container_width=True)

	with st.expander("View All 📝"):
		# result = view_all_data()
		# # st.write(result)
		# result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'deadline_met'])
		# clean_df= result_df[['title', 'task_status', 'deadline']]
		# clean_df['deadline'] = pd.to_datetime(clean_df['deadline'])
		# clean_df['deadline']= clean_df['deadline'].dt.date
		clean_df1= result_df[['title', 'tag', 'task_status', 'deadline_date']]
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))

	# with st.expander("Task Status 📝"):
	# 	task_df = clean_df['task_status'].value_counts().to_frame()
	# 	task_df = task_df.reset_index()
	# 	st.dataframe(task_df)
	# 	p1 = px.pie(task_df,names='task_status',values='count', color='task_status', color_discrete_map={'To-Do':'red', 'Done':'green', 'In-Progress':'orange'})
	# 	st.plotly_chart(p1,use_container_width=True)

footer1_html = """
<br>
<hr>
<div style="
    position: relative;
    inset: 0px auto auto 0px;
    margin-top: 20px;
	margin-left: -100px;
    padding: 10px;
    color: #333;
    text-align: center;
	width: 120%
">
    Made with ❤️ by <strong>Bella & Rita</strong>
</div>
"""
# st.markdown(footer1_html, unsafe_allow_html=True)
st.markdown("<br><hr><center>Made with ❤️ by <strong>Bella & Rita</strong></center>", unsafe_allow_html=True)

# footer()