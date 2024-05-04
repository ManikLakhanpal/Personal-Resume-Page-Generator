from flask import Flask, url_for, redirect, render_template, request
import smtplib
import psycopg2
import credentials # seperate python file with credentials
import json
import os

smtp_server = credentials.smtp_server
email = credentials.email
password = credentials.password

app = Flask(__name__)

connect = psycopg2.connect(
  database="resume",
  user="postgres",
  password=credentials.db_password,
  host="localhost",
  port="5432"
)

cursor = connect.cursor()

def to_dict(key, val):
  return key, val

@app.route('/')
def home():
  return render_template('home.html', hightlight='Home')


@app.route('/about')
def about():
  return render_template('about.html', highlight='About')


@app.route('/contact')
def contact():
  return render_template('contact.html', highlight='contact')


@app.route('/resume', methods=["GET", "POST"])
def resume():

  if request.method == "POST":
    user_name = request.form.get('name')
    user_phone = request.form.get('phone')
    user_email = request.form.get('email')
    user_location = request.form.get('location')
    user_sec_edu = request.form.get('secondary_edu')
    user_sr_edu = request.form.get('senior_secondary_edu')
    user_languages = request.form.get('languages').split(', ')
    user_profile = request.form.get('profile')
    user_achievements = request.form.get('achievements').split(', ')
    user_skills = request.form.get('prof_skills').split(', ')
    user_knowledge = request.form.get('prof_knowledge').split(', ')
    user_hobbies = request.form.get('hobbies').split(', ')
    user_linkedin = request.form.get('linkedin')
    picture = request.form.get('picture')

    lang_name = [i for i in user_languages[::2]]
    lang_val = [i for i in user_languages[1::2]]
    skill_name = [i for i in user_skills[::2]]
    skill_val = [i for i in user_skills[1::2]]
    achi_val = [i for i in user_achievements[::2]]
    achi_txt = [i for i in user_achievements[1::2]]

    lang = dict(map(to_dict, lang_name, lang_val))
    skill = dict(map(to_dict, skill_name, skill_val))
    achi = dict(map(to_dict, achi_val, achi_txt))

    filename = f"{user_name[:5]}{user_phone}"

    try:
      cursor.execute("SELECT * FROM resumes")
      data = cursor.fetchall()

      insert_query = """
        INSERT INTO resumes (
        name, phone, email, linkedin, location,
        secondary_edu, senior_secondary_edu, languages,
        profile, achievements, prof_skills,
        prof_knowledge, hobbies, picture, filename
        )
        VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
        )
      """
      data = (
        user_name, user_phone, user_email, user_linkedin, user_location,
        user_sec_edu, user_sr_edu, user_languages, user_profile,
        user_achievements, user_skills, user_knowledge, user_hobbies, picture, filename
      )

      if len(data) > 0:
        cursor.execute(f"DELETE FROM resumes WHERE filename = '{filename}';")
        cursor.execute(insert_query, data)
        connect.commit()

      else:
        cursor.execute(insert_query, data)
        connect.commit()
  
      with smtplib.SMTP(smtp_server, 587) as connection:
        connection.starttls()
        connection.login(email, password)
        connection.sendmail(
          email, user_email,
          f"Subject:Resume Form Generated\n\nDear, {user_name} Now you can access you resume by clicking on following link:\n\nSite: http://resume.w16manik.ninja/resume/{user_name[:5]}{user_phone}"
        )

      return render_template(
        'resume.html',
        name=user_name,  #done
        phone=user_phone,  #done
        email=user_email,  #done
        location=user_location,  #done
        sec=user_sec_edu,  #done
        sr=user_sr_edu,  #done
        language=lang,  #done
        profile=user_profile,  #done
        achievements=achi,  #done
        skills=skill,  #done
        linkedin=user_linkedin,  #done
        knowledge=user_knowledge,  #done
        picture=picture,  #done
        hobbies=user_hobbies
      )  #done
    
    except Exception as e:
      return f"An error occurred: {str(e)}"
  else:
    return render_template('form.html', highlight='Resume')

@app.route('/resume/<id>')
def load_resume(id):
  try:

    cursor.execute(f"SELECT * FROM resumes WHERE filename = '{id}';")
    n = cursor.fetchone()
    if n:

      lang_name = [i for i in n[7][1:-1].split(',')[::2]]
      lang_val = [i for i in n[7][1:-1].split(',')[1::2]]
      skill_name = [i for i in n[10][1:-1].split(',')[::2]]
      skill_val = [i for i in n[10][1:-1].split(',')[1::2]]
      achi_val = [i for i in n[9][1:-1].split(',')[::2]]
      achi_txt = [i for i in n[9][1:-1].split(',')[1::2]]

      lang = dict(zip(lang_name, lang_val))
      skill = dict(zip(skill_name, skill_val))
      achi = dict(zip(achi_val, achi_txt))

      print(lang_name)
      print(skill)
      print(achi)

      return render_template(
          'resume.html',
          name=n[0],  #done
          phone=n[1],  #done
          email=n[2],  #done
          location=n[4],  #done
          sec=n[5],  #done
          sr=n[6],  #done
          language=lang,  #done
          profile=n[8],  #done
          achievements=achi,  #done
          skills=skill,  #done
          linkedin=n[3],  #done
          knowledge=n[11][1:-1].split(','),  #done
          picture=n[13],  #done
          hobbies=n[12][1:-1].split(','))  #done
    else:
      return "ERROR: User does not exist"
  
  except Exception as e:
        print("Error:", e)
        return "An error occurred while fetching data from the database"

  finally:
    print("Operation complete")


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5004, debug=True)
