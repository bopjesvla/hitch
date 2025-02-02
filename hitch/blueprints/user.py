from flask import Blueprint, current_app, jsonify, redirect, render_template
from flask_security import current_user

from hitch.extensions import security
from hitch.forms import UserEditForm

user_bp = Blueprint("user", __name__)


@user_bp.route("/edit-user", methods=["GET", "POST"])
def form():
    if current_user.is_anonymous:
        return redirect("/login")

    form = UserEditForm()

    if form.validate_on_submit():
        updated_user = security.datastore.find_user(username=current_user.username)
        updated_user.gender = form.gender.data
        updated_user.year_of_birth = form.year_of_birth.data
        updated_user.hitchhiking_since = form.hitchhiking_since.data
        updated_user.origin_country = form.origin_country.data
        updated_user.origin_city = form.origin_city.data
        updated_user.hitchwiki_username = form.hitchwiki_username.data
        updated_user.trustroots_username = form.trustroots_username.data
        security.datastore.put(updated_user)
        security.datastore.commit()
        return redirect("/me")

    form.gender.data = current_user.gender
    form.year_of_birth.data = current_user.year_of_birth
    form.hitchhiking_since.data = current_user.hitchhiking_since
    form.origin_country.data = current_user.origin_country
    form.origin_city.data = current_user.origin_city
    form.hitchwiki_username.data = current_user.hitchwiki_username
    form.trustroots_username.data = current_user.trustroots_username

    return render_template("edit_user.html", form=form)


@user_bp.route("/user", methods=["GET"])
def get_user():
    """Endpoint to get the currently logged in user."""
    current_app.logger.info("Received request to get user.")

    # Check if the user is logged in
    if not current_user.is_anonymous:
        return jsonify({"logged_in": True, "username": current_user.username})
    else:
        return jsonify({"logged_in": False, "username": ""})


# TODO: properly delete the user after their confirmation
@user_bp.route("/delete-user", methods=["GET"])
def delete_user():
    return f"To delete your account please send an email to {current_app.config['EMAIL']} with the subject 'Delete my account'."


def get_origin_string(user):
    origin_string = (
        (user.origin_city if user.origin_city is not None else "")
        + (", " if (user.origin_city != "" and user.origin_city is not None) else " ")
        + (user.origin_country if user.origin_country is not None else "")
    )
    return origin_string


@user_bp.route("/me", methods=["GET"])
def show_current_user():
    if current_user.is_anonymous:
        return redirect("/login")

    user = current_user
    origin_string = get_origin_string(user)

    current_app.logger.info(user.hitchwiki_username is None)
    print(user.hitchwiki_username, type(user.hitchwiki_username))

    return render_template(
        "me.html",
        username=user.username,
        email=user.email,
        gender=user.gender,
        origin_string=origin_string,
        hitchwiki_username=user.hitchwiki_username,
        trustroots_username=user.trustroots_username,
        hitchhiking_since=user.hitchhiking_since,
        year_of_birth=user.year_of_birth,
    )


@user_bp.route("/is_username_used/<username>", methods=["GET"])
def is_username_used(username):
    """Endpoint to check if a username is already used."""
    current_app.logger.info(f"Received request to check if username {username} is used.")

    user = security.datastore.find_user(username=username)

    if user:
        return jsonify({"used": True})
    else:
        return jsonify({"used": False})


@user_bp.route("/account/<username>", methods=["GET"])
def show_account(username):
    current_app.logger.info(f"Received request to show user {username}.")

    user = security.datastore.find_user(username=username)
    if user:
        origin_string = get_origin_string(user)

        return render_template(
            "account.html",
            username=user.username,
            email=user.email,
            gender=user.gender,
            origin_string=origin_string,
            hitchwiki_username=user.hitchwiki_username,
            trustroots_username=user.trustroots_username,
            hitchhiking_since=user.hitchhiking_since,
            year_of_birth=user.year_of_birth,
        )
    else:
        # TODO
        return "User not found."
