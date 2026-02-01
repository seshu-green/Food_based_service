from django import forms

class loginform(forms.Form):
    email = forms.CharField(max_length=128)
    name = forms.CharField(max_length=128)
    passcode = forms.CharField(widget=forms.PasswordInput,max_length=128)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class chatform(forms.Form):
    prompt = forms.CharField(max_length=512, required=False)
    image = forms.ImageField(required=False)
