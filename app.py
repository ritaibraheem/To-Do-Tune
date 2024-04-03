from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd 
from db_funcs import *
from PIL import Image
import plotly.express as px
from model import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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

st.image('TO DO Tune.svg',)

with st.sidebar:
	choice = option_menu("Menu", ["🎯 My Day","✅ Create Task","🖊️ Update Task","❌ Delete Task", "📝 All Tasks"], 
									  icons=[' ', ' ',' ', ' ',' '], menu_icon=' ', default_index=0,
									  styles={
        "container": {"background-color": "#fafafa"},
		"nav-link": {"text-align": "left", "margin":"0px", "--hover-color": "#eee", "font-weight": "normal"},
        "nav-link-selected": {"background-color": "#d0d0d0"}
    })

create_table()

if choice == "🎯 My Day":
	st.subheader("🎯 My Day")

	col_large1,col_large2,col_large3 = st.columns(3,gap='large')
	
	with col_large1:

		feeling_html = """
			<div style="font-size: 85%; padding-bottom:5px;">
				How do you feel today?
			</div>
			"""
		st.markdown(feeling_html, unsafe_allow_html=True)
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
		avg_sleep_hours_int = st.slider('How many hours did you sleep at night?', 0.0, 24.0, 7.0, step=0.25)
		st.write(avg_sleep_hours_int, ' hours.')	

	with col_large3:
		res = st.radio('Do you took medicine today?',['Yes', 'No'],index=None)
		if res=='Yes':
			medication_taken = True
		else:
			medication_taken = False

	tab1, tab2, tab3 = st.tabs(["Today's Tasks 📝", "   🔔   ", "Analysis"])

	with tab1:
		st.text('Do now and live peacefully:')
		result = get_today_tasks(date.today())
		result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late'])
		clean_df1= result_df[['title', 'tag', 'about', 'task_status', 'deadline_date']]
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))

	with tab2:
		st.header("What to do next? ")
		model_result = run_ml_model()
		st.text(model_result) 
		
	with tab3:
		st.header("Your Monthly Behavior")
		
		result = view_all_data()
		result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late'])
		
		done_tasks = result_df[(result_df['task_status']=='Done')]
		done_tasks['deadline_date']=pd.to_datetime(done_tasks['deadline_date']) 
		done_tasks['end_time']=pd.to_datetime(done_tasks['end_time'])
		done_tasks = done_tasks[['title','tag','deadline_date','end_time','is_late']]
		done_tasks['is_late'] = done_tasks['is_late'].astype('int64')

		late_done_tasks = done_tasks[(done_tasks['is_late']==1)]
		on_time_done_tasks = done_tasks[(done_tasks['is_late']==0)]

		
		one_month_later = date.today() + relativedelta(months=2)

		fig = make_subplots(rows=1, cols=2)

		trace0 = go.Histogram(x=late_done_tasks['deadline_date'],
							name='Lated Tasks',
							xbins=dict(
							start='2023-11-01',
							end=str(one_month_later),
							size= 'M1'), # 1 months
							autobinx = False
							)
		# trace1 = go.Histogram(x=x, nbinsx = 8)
		trace1 = go.Histogram(x=on_time_done_tasks['deadline_date'],
							name='On-Time Tasks',
							xbins=dict(
							start='2023-11-01',
							end=str(one_month_later),
							size= 'M1'), # 1 months
							autobinx = False
							)

		fig.append_trace(trace0, 1, 1)
		fig.append_trace(trace1, 1, 2)

		fig.update_layout(title = {"text": "Completed Tasks Distribution Over The Time","x": 0.4, })

		st.plotly_chart(fig,use_container_width=True)

		# late_done_tasks['deadline_month'] = late_done_tasks['deadline_date'].dt.month
		# late_done_tasks['end_month'] = late_done_tasks['end_time'].dt.month
		# late_done_tasks['deadline_year'] = late_done_tasks['deadline_date'].dt.year

		# on_time_done_tasks['deadline_month'] = on_time_done_tasks['deadline_date'].dt.month
		# on_time_done_tasks['end_month'] = on_time_done_tasks['end_time'].dt.month
		# on_time_done_tasks['deadline_year'] = on_time_done_tasks['deadline_date'].dt.year

		# on_time_done_tasks_gb = on_time_done_tasks.groupby(['deadline_year','deadline_month']).size()
		# late_done_tasks_gb = late_done_tasks.groupby(['deadline_year','deadline_month']).size()

		# monthly_late_tasks = late_done_tasks_gb.reset_index()
		# monthly_on_time_tasks = on_time_done_tasks_gb.reset_index()


if choice == "✅ Create Task":
	st.subheader("Add New Task")
	col1,col2 = st.columns(2)

	with col1:
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
				is_late = True 
			else: is_late = False
	else:
		end_time=None
		is_late = None

	if st.button("Add Task"):
		add_row(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late)
		st.success("Added Task \"{}\" ✅".format(title))
		st.balloons()

elif choice == "🖊️ Update Task":
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

		if st.button("🖊️ Update Task"):
			edit_task_data(new_task,new_task_status,new_task_due_date,task,task_status,task_due_date)
			st.success("Updated Task \"{}\" ✅".format(task,new_task))

		with st.expander("View Updated Data 💫"):
			result = view_all_data()
			clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
			st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

elif choice == "❌ Delete Task":
	st.subheader("Delete")
	with st.expander("View Data"):
		result = view_all_data()
		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

	unique_list = [i[0] for i in view_all_task_names()]
	delete_by_task_name =  st.selectbox("Select Task",unique_list)
	if st.button("Delete ❌"):
		delete_data(delete_by_task_name)
		st.warning("Deleted Task \"{}\" ✅".format(delete_by_task_name))

	with st.expander("View Updated Data 💫"):
		result = view_all_data()
		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))

elif choice == "📝 All Tasks":
	result = view_all_data()
	result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late'])
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
		clean_df1= result_df[['title', 'tag', 'task_status', 'deadline_date']]
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))

