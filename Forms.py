from wtforms import Form, StringField, TextAreaField, DecimalField, validators, IntegerField, BooleanField, SubmitField, \
    SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms.fields.html5 import DateField, EmailField
from flask_wtf import FlaskForm
plist = list()


# Online Pharmacy
class CreateItemForm(Form):
    name = StringField('Name: ', [validators.Length(min=1, max=50), validators.DataRequired()], default='')
    price = DecimalField('Price($): ', [validators.NumberRange(min=1), validators.DataRequired()], default=0, places=2)
    have = IntegerField('Amount we have in stock: ', [validators.NumberRange(min=1), validators.DataRequired()],
                        default=0)
    picture = StringField('Picture (link): ', [validators.Length(min=1, max=500), validators.DataRequired()],
                          default='')
    bio = TextAreaField('Item Description: ', [validators.DataRequired()], default='')
    prescription = BooleanField('Prescription', default=False)


class BuyItemForm(Form):
    want = IntegerField('Quantity: ', [validators.NumberRange(min=1), validators.DataRequired()], default=0)


class CheckoutForm(Form):
    name = StringField('Name on Card: ', [validators.Length(min=1, max=150), validators.DataRequired()], default='')
    card_no = StringField('Card Number: ', [validators.Length(min=1, max=150), validators.DataRequired()],
                          default='')
    cvn = StringField('Card Verification Number: ', [validators.Length(min=1, max=150), validators.DataRequired()],
                      default='')
    exp = StringField('Expiry Date', [validators.Length(min=3, max=5), validators.DataRequired()])
    address = StringField('Address: ', [validators.Length(min=1, max=150), validators.DataRequired()], default='')
    # Use Sting field as Postal Code needs to be saved as string as integer removes front 0 i.e 081456 = 81456
    postal_code = StringField('Postal Code: ', [validators.Length(min=6, max=6), validators.DataRequired()], default='')


class PrescriptionForm(Form):
    quantity = IntegerField('', [validators.NumberRange(min=1), validators.DataRequired()])
    dosage_times = IntegerField('', [validators.NumberRange(min=1), validators.DataRequired()])
    dosage_interval = SelectField('', [validators.DataRequired()],
                                  choices=[('', 'Select'), ("An Hour", "An Hour"), ("A Day", "A Day")], default='')


class PrescribeForm(Form):
    patient_nric = StringField("Patient's NRIC:", [validators.DataRequired()])


# ContactUs Forms
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired()])
    enquiries = TextAreaField("Enquiries ", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FAQ(Form):
    question = StringField('Question', [validators.Length(min=1), validators.DataRequired()])
    answer = TextAreaField('Answer', [validators.Length(min=1), validators.DataRequired()])
    date = DateField('Date', [validators.DataRequired()], format='%Y-%m-%d')


# Search Bar
class SearchBar(Form):
    search = StringField('')
    history = SelectField('',
                          choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)],
                          default=2)


# Application
class CreateApplicationForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    lname = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    nric = StringField('NRIC / FIN', [
        validators.Regexp('^[SsTtFfGg][0-9]{7}[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]$',
                          message='Invalid NRIC. e.g.S1234567A'),
        validators.DataRequired()])  # need to validate
    email = EmailField('Email', [validators.Length(min=1, max=150), validators.DataRequired(), validators.Email()])
    age = IntegerField('Age', [validators.number_range(min=17, max=70), validators.DataRequired()])
    address = StringField('Address', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()],
                         choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female')], default='')
    nationality = StringField('Nationality', [validators.Length(min=1, max=150), validators.DataRequired()])
    language = StringField('Language', [validators.Length(min=1, max=150), validators.DataRequired()])
    phoneno = IntegerField('Phone Number',
                           [validators.number_range(min=60000000, max=999999999,
                                                    message="Singapore's Phone Number must be 8 numbers only"),
                            validators.DataRequired()])  # need to validate
    quali = SelectField('Highest Qualification', [validators.DataRequired()],
                        choices=[('', 'Select'), ("O'Levels", "O'Levels"), ("N'Levels", "N'Levels"),
                                 ("A'Levels", "A'Levels"), ('Diploma', 'Diploma'), ('Bachelor', 'Bachelor'),
                                 ('Master', 'Master')], default='')
    industry = SelectField('Industry', [validators.DataRequired()], choices=[('', 'Select'), ("Tourism", "Toursim"), (
        "BioMedical Science", "BioMedical Science"),
                                                                             ("Logistics", "Logistics"),
                                                                             ('Banking & Finance', 'Banking & Finance'),
                                                                             ('Chemicals', 'Chemicals'),
                                                                             ('Construction', 'Construction'),
                                                                             ('Casino', 'Casino'),
                                                                             ('Healthcare', 'Healthcare'),
                                                                             ('Education', 'Education'),
                                                                             ('ICT & Media', 'ICT & Media'),
                                                                             ('Null', 'Null')], default='')
    comp1 = StringField('Company', [validators.Length(min=1, max=150), validators.DataRequired()])
    posi1 = StringField('Position', [validators.Length(min=1, max=150), validators.DataRequired()])
    comp2 = StringField('Company (optional)', [validators.Length(min=1, max=150), validators.optional()])
    posi2 = StringField('Position (optional)', [validators.Length(min=1, max=150), validators.optional()])


class ResendForm(Form):
    nric = RadioField("NRIC/FIN", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    email = RadioField("Email", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    age = RadioField("Age", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    gender = RadioField("Gender", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    nationality = RadioField("Nationality", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    language = RadioField("Language", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    phoneno = RadioField("Phone Number", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    quali = RadioField("Qualification", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])
    industry = RadioField("Industry", [validators.optional()], choices=[('Yes', 'Yes'), ('No', 'No')])


# User Forms
class RegisterForm(Form):
    NRIC = StringField("NRIC",
                       [validators.DataRequired(), Regexp('^[ST][0-9]{7}[ABCDEFGHIZJ]$', message='Invalid NRIC')])
    FirstName = StringField("First Name", [validators.DataRequired(), validators.Length(min=1, max=150)])
    LastName = StringField("Last Name", [validators.DataRequired(), validators.Length(min=1, max=150)])
    Gender = SelectField('Gender', [validators.DataRequired()],
                         choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    Dob = DateField('Date of Birth', [validators.DataRequired()])
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    #Edited by Suja
    Password = PasswordField("Password",
                             [validators.DataRequired(), Regexp('^[ABCDEFGHIJKLMNOPQRSTUVWXYZ]{1}[abcdefghijklmnopqrstuvwxyz]{3}[0-9]{4}[!@#$%&*?]{1}$', message='Invalid Password, '
                                                                                                                         'Must contain at least 1 uppercase letter, '
                                                                                                                         'Must contain at least 1 lowercase letter, '
                                                                                                                         'Must contain at least one number, '
                                                                                                                         'Must contain at least one special character, '), Length(min=8, max=30, message="Invalid Password Length")])
    Confirm = PasswordField("Confirm Password", [validators.DataRequired(), validators.EqualTo("Password")])
    URL = StringField("URL", [validators.optional()])
    specialization = StringField("Specialization", [validators.optional()])


class LoginForm(Form):
    NRIC = StringField("NRIC", [validators.DataRequired(), validators.Length(min=9, max=9)])
    Password = PasswordField("Password", [validators.DataRequired()])


class UpdateProfileForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    Dob = DateField('Date of Birth', [validators.DataRequired()])


class ChangePasswordForm(Form):
    old_password = PasswordField("Current Password", [validators.DataRequired()])    # edited by Jabez
    Password = PasswordField("New Password", [validators.DataRequired()])
    Confirm = PasswordField("Confirm New Password", [validators.DataRequired()])


class ResetPasswordForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])


class AdminUpdateForm(Form):
    Email = StringField("Email", [validators.DataRequired(), validators.Email()])
    Password = PasswordField("Password",
                             [validators.DataRequired(), Length(min=8, max=30, message="Invalid Password Length")])
    URL = StringField("URL", [validators.optional()])


# Appointment Form
class AppointmentForm(Form):
    Department = SelectField("Department", [validators.DataRequired()],
                             choices=[('', 'Select'), ('Cardiology', 'Cardiology'),
                                      ('Gastroenterology', 'Gastroenterology'),
                                      ('Haematology', 'Haematology')])
    Date = DateField("Appointment Date", [validators.DataRequired()], format='%Y-%m-%d')
    Time = SelectField("Appointment Time", [validators.DataRequired()],
                       choices=[('', 'Select'), ('8:00:00', '8AM'), ('10:00:00', '10AM'), ('12:00:00', '12PM'),
                                ('14:00:00', '2PM'), ('16:00:00', '4PM'),
                                ('18:00:00', '6PM'), ('20:00:00', '8PM'), ('22:00:00', '10PM')], default='')
    Type = SelectField("Appointment Type", [validators.DataRequired()],
                       choices=[('', 'Select'), ('E-Doctor', 'E-Doctor'), ('Visit', 'Visit')])


class DocAppointmentForm(Form):
    def __init__(self, form, patient_list):
        global plist
        super().__init__(form)
        plist = patient_list


    Department = SelectField("Department", [validators.DataRequired()],
                             choices=[('', 'Select'), ('Cardiology', 'Cardiology'),
                                      ('Gastroenterology', 'Gastroenterology'),
                                      ('Haematology', 'Haematology')])
    Date = DateField("Appointment Date", [validators.DataRequired()], format='%Y-%m-%d')
    Time = SelectField("Appointment Time", [validators.DataRequired()],
                       choices=[('', 'Select'), ('8:00:00', '8AM'), ('10:00:00', '10AM'), ('12:00:00', '12PM'),
                                ('14:00:00', '2PM'), ('16:00:00', '4PM'),
                                ('18:00:00', '6PM'), ('20:00:00', '8PM'), ('22:00:00', '10PM')], default='')
    Type = SelectField("Appointment Type", [validators.DataRequired()],
                       choices=[('', 'Select'), ('E-Doctor', 'E-Doctor'), ('Visit', 'Visit')])
