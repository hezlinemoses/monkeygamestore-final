
from django.shortcuts import render,redirect
from products.models import GameDescription, Category, Game, GameMedia
from products.forms import CategoryCreationForm, DescEditFormset,GameCreationForm, GameDescForm, GameDescFormset, GameMediaEditFormset, GameMediaFormset, SubCategoryCreationForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify

# Create your views here.

@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_category_list_view(request):
    categories = Category.objects.filter(parent_category = None)
    context= {
        'categories':categories,
    }
    return render(request,'adminpanel/admin_categories.html',context)


@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_addcategory_view(request):
    if request.method == 'POST':

        form = CategoryCreationForm(request.POST)
        if form.is_valid():
            form.save()
            name= form.cleaned_data.get('name')
            messages.success(request,f"{name}  added successfuly")
            return redirect('admin_categorylist')
    else:
        form =CategoryCreationForm()
    context ={
        'form':form,
    }
    return render(request,'adminpanel/admin_addcategory.html',context)



@never_cache
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_category_edit_view(request, slug):
    try:
        category_edit = Category.objects.get(slug = slug)
    except Category.DoesNotExist:
        return redirect('admin_categorylist')
        
    
   
    form = CategoryCreationForm(instance = category_edit)
    if request.method == 'POST':
        form = CategoryCreationForm(request.POST, instance = category_edit)

        if form.is_valid():
            slug = slugify(form.cleaned_data.get('name'))
            category_edit.slug = slug
            form.save()
            messages.success(request, f'{category_edit.name} updated succesfully.')
            return redirect('admin_editcategory',id)
    
    context ={
        'category_edit':category_edit,
        'form':form,
        }

    return render(request, "adminpanel/admin_editcategory.html", context)

@never_cache
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def subcategory_add_view(request,slug):
    try:
        main_category = Category.objects.get(slug=slug)
    except:
        return redirect('admin_categorylist')
    
    id = main_category.id
    form = SubCategoryCreationForm(id)
    if request.method == 'POST':
        form = SubCategoryCreationForm(id,request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_categorylist')

    context = {
        'form' : form,
    }
    return render(request,'adminpanel/admin_addsubcat.html',context)


@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_category_disable(request,slug):
    category = Category.objects.get(slug = slug)
    # if request.method == 'POST':
    if category.is_active:
        category.is_active = False
        category.save()
        messages.success(request,f"{category} disabled successfuly")
    else:
        category.is_active = True
        category.save()
        messages.success(request,f"{category} enabled successfuly")
        
    return redirect('admin_categorylist')


@never_cache
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_listgame_view(request):
    games = Game.objects.all()
    context={
        'games':games,
    }
    return render(request,'adminpanel/admin_games.html',context)



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_addgame_view(request):
    form = GameCreationForm()
    qs = GameDescription.objects.none()
    formset = GameDescFormset(queryset=qs)
    qs2 = GameMedia.objects.none()
    imgformset = GameMediaFormset(queryset=qs2,prefix='image')
    if request.method == 'POST':
        form = GameCreationForm(data = request.POST, files = request.FILES,)
        formset = GameDescFormset(request.POST)
        imgformset = GameMediaFormset(data=request.POST, files = request.FILES,prefix='image')
        if all([form.is_valid(),formset.is_valid(),imgformset.is_valid()]):
            # game = form.save(commit = False)
            game: Game = form.save()
            # game.save()

            for form in formset:
                desc:GameDescription = form.save(commit=False)
                desc.game = game
                desc.save()
            for imgform in imgformset:
                img:GameMedia = imgform.save(commit=False)
                img.game = game
                img.save()
            game_categories = game.categories.all()
            for category in game_categories:
                if category.category_offer.filter(status="Ongoing").exists():
                    game.discount_status = 'Category Discount'
                    game.save()
                    game.discount
            messages.success(request,"Game added successfuly")
            return redirect('admin_gamelist')
        else:
            form = GameCreationForm()
            formset = GameDescFormset()
    context={
        'form': form,
        'formset': formset,
        'imgformset': imgformset,
    }
    return render(request,'adminpanel/admin_addgame.html',context)



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def admin_editgame_view(request,id):
    try:
        game_edit = Game.objects.get(id = id)
    except Game.DoesNotExist:
        return redirect('admin_gamelist')
    
    form = GameCreationForm(instance=game_edit)
    qs = game_edit.descriptions.all()
    formset = DescEditFormset(queryset=qs)
    qs2 = game_edit.medias.all()
    imgformset = GameMediaEditFormset(queryset=qs2,prefix='image')
    if request.method == 'POST':
        form = GameCreationForm(data = request.POST, files = request.FILES,instance=game_edit)
        
        formset = DescEditFormset(request.POST)
        imgformset = GameMediaEditFormset(data=request.POST, files = request.FILES,prefix='image')
        if all([form.is_valid(),formset.is_valid(),imgformset.is_valid()]):
            # game = form.save(commit = False)
            game: Game = form.save()
            # game.save()

            for form in formset:
                desc:GameDescription = form.save(commit=False)
                desc.game = game
               
                if form.cleaned_data["DELETE"]==True:
                    try:
                        desc.delete()
                    except:
                        pass
                else:
                    desc.save()
            for imgform in imgformset:
                img:GameMedia = imgform.save(commit=False)
                img.game = game
               
                if imgform.cleaned_data["DELETE"]==True:
                    try:
                        img.delete()
                    except:
                        pass
                else:
                    img.save()
        
            
            messages.success(request,f"{game_edit.title} updated successfuly")
            return redirect('admin_gamelist')

            
   
    context ={
        'game_edit':game_edit,
        'form':form,
        'formset': formset,
        'imgformset': imgformset,
        }

    return render(request, "adminpanel/editgame.html", context)



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def game_block_view(request,id):
    blockgame = Game.objects.get(id=id)

    if blockgame.is_active:
        blockgame.is_active = False
        blockgame.save()
        messages.success(request,f"{blockgame.title}  disabled successfully")
    else:
        blockgame.is_active =True
        blockgame.save()
        messages.success(request,f"{blockgame.title}  enabled successfully")
    return redirect('admin_gamelist')

@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def delete_category(request, slug):
    try: 
        cat_delete = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        messages.error(request,f"Category doesn't exist")


    
    if cat_delete is not None:
        cat_delete.delete()
        messages.success(request,f"{cat_delete.name}  deleted successfully")
    return redirect('admin_categorylist')



@never_cache
@user_passes_test(lambda u:u.is_superuser, login_url="admin_login")
def delete_game(request,id):
    try:
         game = Game.objects.get(id=id)
    except:
        messages.error(request,f"Game doesn't exist")

    if game is not None:
        game.main_banner.delete()
        game.thumbnail.delete()
        game.delete()
        messages.success(request,f"{game.title} deleted successfully")
    return redirect('admin_gamelist')


