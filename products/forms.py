from django import forms
from django.forms import ModelForm
from products.models import Game, Category , GameDescription, GameMedia
from django.forms import modelformset_factory


class CategoryCreationForm(forms.ModelForm):
    # parent_category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'),required=False,help_text="Select the parent article (if any)")
    class Meta:
        model = Category
        fields = ("name","description")
        labels = {
            'name' : 'Category Name',
            'description' : 'Description',
            'parent_category' : 'Main Category',
        }
        widgets = {
            'name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter category name',
                
            }),
            'description' : forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':'Enter description',
                'rows': '3',
            }),
            # 'parent_category': forms.ChoiceField(),
            
        }

        

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     self.fields['parent_category'].disabled = True
        #     self.fields['name'].disabled = True



class SubCategoryCreationForm(forms.ModelForm):
    # parent_category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'),required=False,help_text="Select the parent article (if any)")
    class Meta:
        model = Category
        fields = ("parent_category","name","description",)
        labels = {
            'name' : 'Sub-category Name',
            'description' : 'Sub-category description',
            'parent_category' : 'Main Category',
        }
        widgets = {
            'name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Sub-category name',
            }),
            'description' : forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':'Enter sub-category description',
                'rows': '3',
            }),
            
        }
    def __init__(self, id, *args, **kwargs):
        super(SubCategoryCreationForm, self).__init__(*args, **kwargs)
        self.fields['parent_category'].queryset = Category.objects.filter(id=id)
        self.fields['parent_category'].required = True
    





class GameCreationForm(forms.ModelForm):

    class Meta:
        model = Game
        fields =('title','categories','base_price','main_banner','thumbnail',)

        categories = forms.ModelChoiceField(
            queryset=Category.objects.all(),
        )

     

    def __init__(self, *args, **kwargs):
        super(GameCreationForm, self).__init__(*args, **kwargs)
        self.fields['main_banner'].widget.attrs.update({'class': 'form-control','id':'id_image1','name':'image', 'onchange':"changeImg(this.id)"}) 
        self.fields['title'].widget.attrs.update({'class': 'form-control','required':''})
        self.fields['categories'].widget.attrs.update({'class': 'form-control',})
        self.fields['base_price'].widget.attrs.update({'class': 'form-control',})
        self.fields['thumbnail'].widget.attrs.update({'class': 'form-control','onchange':"changeImg(this.id)"})
        # self.fields['thumbnail'].widget.attrs.update({'class': 'form-control','id':'id_image1','name':'image', 'onchange':"changeImg(event)"})

   
class GameDescForm(forms.ModelForm):
    description = forms.CharField(max_length=700,required=True,widget=forms.Textarea())
    class Meta:
        model = GameDescription
        fields =('heading','description')
        
        def __init__(self, *args, **kwargs):
            super(GameDescForm, self).__init__(*args, **kwargs)
            self.fields['heading'].widget.attrs.update({'class': 'form-control','required': ''})
            self.fields['description'].widget.attrs.update({'class': 'form-control',})


class GameMediaCreationFrom(forms.ModelForm):

    class Meta:
        model = GameMedia
        fields=('slideimage',)
    
    def __init__(self, *args, **kwargs):
        super(GameMediaCreationFrom, self).__init__(*args, **kwargs)
        self.fields['slideimage'].widget.attrs.update({'class': 'form-control','name':'slideimage', 'onchange':"changeImg(this.id)"}) 





GameDescFormset = modelformset_factory(GameDescription,form = GameDescForm,extra=1,min_num=0)
DescEditFormset = modelformset_factory(GameDescription,form = GameDescForm,extra=0,can_delete=True)
GameMediaFormset = modelformset_factory(GameMedia, form=GameMediaCreationFrom, extra = 1)
GameMediaEditFormset = modelformset_factory(GameMedia,form = GameMediaCreationFrom,extra=0,can_delete=True)