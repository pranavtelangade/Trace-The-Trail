from flask import session, render_template, request, redirect, url_for
from flask import Blueprint
from project.apps.face_detection.models import UserProfile

bp = Blueprint('view', __name__, url_prefix='/face_detection')

@bp.route('/login', methods=["GET", "POST"])
def validate_user():
    if request.method=='GET':
        return render_template('login.html', error='')
    
    else:
        request_data = request.form.to_dict()
        user_name = request_data.get('user_name')
        password = request_data.get('user_pass')
        user_obj = UserProfile.query.filter_by(user_name=user_name, password=password).first()
        if user_obj:
            session['logged_in']=True
            return redirect(url_for('detection_view.home'))

        return render_template('login.html', error='Sorry! you dont have access')
        
