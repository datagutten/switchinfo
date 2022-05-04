from django import forms


class SearchForm(forms.Form):
    ip = forms.CharField(label='IP', required=False)
    mac = forms.CharField(label='MAC', required=False)
    neighbor = forms.CharField(label='CDP/LLDP neighbor', required=False)
