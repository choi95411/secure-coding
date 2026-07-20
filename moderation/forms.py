from django import forms


class ReportForm(forms.Form):
    reason = forms.CharField(
        min_length=5, max_length=1000, widget=forms.Textarea(attrs={"rows": 4})
    )


class ModerationActionForm(forms.Form):
    action = forms.ChoiceField(choices=())
    reason = forms.CharField(
        min_length=5, max_length=1000, widget=forms.Textarea(attrs={"rows": 3})
    )

    def __init__(self, *args, choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["action"].choices = choices
