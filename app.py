import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt

from userDB.userDB import create_usertable, add_userdata, get_userdata, view_all_users, delete_usertable
from epm.graph import *

def main():
    components.html(
        """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css" integrity="sha384-zCbKRCUGaJDkqS1kPbPd7TveP5iyJE0EjAuZQTgFLD2ylzuqKfdKlfG/eSrtxUkn" crossorigin="anonymous">
        <div class="row">
            <div class="alignleft" style="text-align: justify;">
                <svg width="70" height="40" viewBox="0 0 180 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect y="165" width="180" height="15" rx="5" fill="#D1D5DB"/>
                    <rect y="3" width="37" height="156" rx="5" fill="#7ACBCD"/>
                    <rect x="45" y="3" width="37" height="156" rx="5" fill="#FB8282"/>
                    <rect x="88" y="13.2224" width="37" height="156" rx="5" transform="rotate(-20.9382 88 13.2224)" fill="#7B61FF"/>
                </svg>            
            </div>
            <div class="alignleft" style="text-align: justify;">
                <h1>Educational Process Mining</h1>            
            </div>
        </div>
        """
    )

    menu = ['Home', 'Log In', 'Sign Up', 'About']
    choice = st.sidebar.selectbox('Menu', menu)

    if choice == 'Home':
        # tentative
        if st.sidebar.checkbox('Delete UserDB'):
            delete_usertable()
        
        # tentative
        st.subheader("User Profiles")
        create_usertable()
        user_result = view_all_users()
        if user_result:
            clean_db = pd.DataFrame(user_result, columns=['Username', 'Password', 'Role'])
            st.dataframe(clean_db)
        else:
            st.warning('No data in userDB') 
        page_home()

    elif choice == 'Log In':
        st.sidebar.subheader('Log In')

        role = st.sidebar.selectbox('Student or Instructor?', ['Student', 'Instructor'])
        username = ""
        if role == 'Instructor':
            username = st.sidebar.text_input('ID', placeholder='admin')
        else:
            student_ids = list(range(1,116))
            username = st.sidebar.selectbox('Student ID', student_ids)
        password = st.sidebar.text_input('Password', type="password", placeholder='password for your ID')

        if st.sidebar.checkbox("Log In"):
            create_usertable()
            result = get_userdata(username, password, role)

            if result and role == 'Instructor':

                st.sidebar.success(f"Welcome to the instructor page, {username}")
                page_instructor()

            elif result and role == 'Student':
                st.sidebar.success(f"Welcome to the student page, {username}")
                page_student(username)

            else:
                st.sidebar.warning("Incorrect Username/Password")
                

    elif choice == 'Sign Up':
        st.subheader("Create New Account")
        new_role = st.selectbox('Student or Instructor?', ['Student', 'Instructor'])
        new_username = ""
        if new_role == 'Instructor':
            new_username = st.text_input('ID', placeholder='admin')
        else:
            student_ids = list(range(1,116))
            new_username = st.selectbox('Student ID', student_ids)
        new_password = st.text_input("Password", type='password')

        if st.button("Sign Up"):
            create_usertable()
            add_userdata(new_username, new_password, new_role)
            new_userdata = get_userdata(new_username, new_password, new_role)
            if new_userdata:
                st.success("You have successfully created a valid account")
                st.info("Go to Login Menu to login")
            else:
                st.warning("The inserted ID is already taken. Try a different ID")

    else:
        page_about()



def page_home():
    st.header("Home")


# --- Student Page ---
def page_student(username):
    st.header("Student page")
    option = st.selectbox("Options to choose", ['Behavior Analysis', 'Grades', 'Review Alert'])
    student = int(username)
    if option == 'Behavior Analysis':
        st.header("Behavior Analysis")
        # read in dataframe
        df = session_agg()
        df_avg = session_avg(df)

        # Selectbox - log activity selection
        log_activity = ['mouse_click_left','mouse_wheel', 'idle_time', 
                        'mouse_wheel_click','mouse_click_right',
                        'mouse_movement','keystroke']
        option = st.selectbox(
        '1. Which log activity you like to focus on?',
        log_activity)

        # Multiselect - Activity selection
        sorted_activity_unique = sorted( df['activity'].unique() )
        selected_activity = st.multiselect('2. Which activity do you want to include', 
                                                sorted_activity_unique,
                                                sorted_activity_unique)
        
        # --- Class Average Plot ---
        p = plot_log(df_avg, student, selected_activity, option, type='average').properties(
            title = 'Class Average')

        # --- Student Activity Distribution Plot ---
        s = plot_log(df, student, selected_activity, option, type='student').properties(
            title='Student' + ' ' + str(student) + ' ' + option)

        # Present graphs side by side
        x = alt.hconcat(
            p, s
        ).resolve_scale(y='shared')
        st.write('**Plot Result**: You select ' + option)
        st.write(x)

    elif option == 'Grades':
        st.header("Grades")
        # --- each session histogram plot ---
        session = st.radio('Which session?', (2, 3, 4, 5, 6), 0)
        
        # prepare datasets
        data_for_hist = mid_hist(session)
        data_summary = mid_summary(student, data_for_hist)

        p = plot_mid_hist(session, student, data_for_hist, data_summary)

        st.write(p)
        # --- session grades plot ---
        # prepare datasets
        all, area = mid_avg()

        all = all[all['Student Id'].isin(['Average',str(student)])]

        m = plot_mid(all, area)

        st.write(m)
    else:
        st.header("Review Alert")

# --- Instructor Page ---
def page_instructor():
    st.header("This is the instructor page")
    option = st.selectbox("Options to choose", ['Class Behavior Analysis', 'Class Grades', 
                                                'Grouping Assistant', 'User Profiles'])
    
    if option == 'Class Behavior Analysis':
        # read in dataframe
        df = session_agg()
        df_avg = session_avg(df)

        # Slider - Student Slider 
        student = st.slider('1. Which student?', 1, 115)

        # Selectbox - log activity selection
        log_activity = ['mouse_click_left','mouse_wheel', 'idle_time', 
                        'mouse_wheel_click','mouse_click_right',
                        'mouse_movement','keystroke']
        option = st.selectbox(
        '2. Which log activity you like to focus on?',
        log_activity)

        # Multiselect - Activity selection
        sorted_activity_unique = sorted( df['activity'].unique() )
        selected_activity = st.multiselect('3. Which activity do you want to include', 
                                                sorted_activity_unique,
                                                sorted_activity_unique)

        # --- Class Average Plot ---
        p = plot_log(df_avg, student, selected_activity, option, type='average').properties(
            title = 'Class Average')

        # --- Student Activity Distribution Plot ---
        s = plot_log(df, student, selected_activity, option, type='student').properties(
            title='Student' + ' ' + str(student) + ' ' + option)

        # Present graphs side by side
        x = alt.hconcat(
            p, s
        ).resolve_scale(y='shared')

        st.write('**Plot Result**: You select ' + 'student ' + str(student) + ' and ' + option)
        st.write(x)

    elif option == 'Class Grades':
        st.header("Class Grades")
        # --- each session histogram plot ---
        col1, col2 = st.columns(2)
        with col1:
            session = st.radio('Which session?', (2, 3, 4, 5, 6), 0)
        with col2:
            student = st.number_input('Which student you want to focus on \
                                      (input student ID from 1 to 115)', 1, 115, 1)
        
        # prepare datasets
        data_for_hist = mid_hist(session)
        data_summary = mid_summary(student, data_for_hist)

        p = plot_mid_hist(session, student, data_for_hist, data_summary)

        st.write(p)
        # --- session grades plot ---
        # prepare datasets
        all, area = mid_avg()

        students = all['Student Id'].unique()
        selected_students = st.multiselect('Students you selected', 
                                                students,
                                                ['Average', '1'])
        all = all[all['Student Id'].isin(selected_students)]

        m = plot_mid(all, area)

        st.write(m)

    elif option == 'Grouping Assistant':
        st.header("Grouping Assistant")

    else:
        st.subheader("User Profiles")
        user_result = view_all_users()
        clean_db = pd.DataFrame(user_result, columns=['Username', 'Password'])
        st.dataframe(clean_db)        



def page_about():
    st.header("About page")

def page_behavior_analysis(id):
    st.header("Behavior Analysis")

def page_grades(id):
    st.header("Grades")

def page_review_alert(id):
    st.header("Review Alert")

if __name__ == "__main__":
    main()
