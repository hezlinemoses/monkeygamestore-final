var updateBtns = document.getElementsByClassName('update-cart')

for(var i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click', function(){
        var gameId = this.dataset.game
        var action = this.dataset.action

        if(user === 'AnonymousUser'){
            updateUserCart(gameId, action)
        }
        else{
            updateUserCart(gameId, action)
        }
        
    })
}

function updateUserCart(gameId, action) {
    console.log('GameId:',gameId,'Action:',action)

    var url = '/cart/update/'

    fetch(url, {
        method:'POST',
        headers:{
            'content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'gameId': gameId,'action': action})
    })
    .then((response) => {
        return response.json()
    })
    .then((data)=>{
        // console.log('data from view function:',data)
        if(data.message)
        {
            toastr.success(data.message);
        }
        if(data.message_error)
        {
            toastr.error(data.message_error);
        }
        if(data.add){
            toastr.success(data.add);
        }
        if(data.remove){
            $('.coupon-button').remove();
            $('.coupon-button-container').append(`<button type="button" class="btn btn-sm btn-outline-success btn-lg btn-block coupon-button" onclick='check_coupon()'>Apply Coupon</button>`);
            
            if(data.coupon_messsage){
                toastr.error(data.coupon_messsage);
                $("#coupon_code").attr('class', 'is-invalid form-control');
            }
            toastr.success(data.remove);
        }
        
       
    })
}



function removeItem (id){
    setTimeout(() => {
        $.ajax({
            // data: $(this).serialize(), // get the form data{
            data:{greet:'Hello from client'},
            url: "/cart/counter",
            // on success
            success: function (response) {
                    
                    $("#cart-count").html(response.cart_count);
                    $(".cart-total").html(`₹${response.cart_total}`);
                    $(`#${id}`).closest('.cartitem').attr('class','hidden');
                    
                    if(response.cart_count <=0){
                        $("#empty-cart").attr('class', 'display');
                        $('#shop-more > button').attr('class','btn btn-primary btn-lg btn-block');
                        $(".items-container").attr('class', 'hidden');
                        $('#checkout-btn').attr('class','hidden');
                        $('.apply-coupon').attr('class','hidden');
                        $('.redeemable-button').attr('class','hidden');
                    }

    
            },
            // on error
            error: function (response) {
                // alert the error if any error occured
                console.log(response.responseJSON.errors)
            }
        });
    }, 100);
  }

// var updateQuanBtns = document.getElementsByClassName('update-quantity')
// for(var i = 0;i<updateQuanBtns.length;i++){
//     updateQuanBtns[i].addEventListener('click',function(){
//         var itemId = this.dataset.item
//         var action = this.dataset.action
//         updateQuantity(itemId,action)
//     })
// }


function updateQuantity(itemId,action){
    console.log(itemId);
    console.log(action);
    $.ajax({
        data:{'itemId':itemId,'action':action},
        url:"/cart/updatequantity/",
        success: function(response){
          
            if(response.message){
                toastr.error(response.message);
                console.log(response.message);
            }
            if(response.cart_total){
                $(".cart-total").html(`₹${response.cart_total}`);
            }
            if(response.item_quantity){
                $(`input[name='quantity-${itemId}']`).val(response.item_quantity);
            }
            if(response.removed == true){
                $('.coupon-button').remove();
                $('.coupon-button-container').append(`<button type="button" class="btn btn-sm btn-outline-success btn-lg btn-block coupon-button" onclick='check_coupon()'>Apply Coupon</button>`);
                $("#coupon_code").attr('class', 'form-control is-invalid');
            }
            if(response.item_quantity == 1 ){
                $(`#remove-btn-${itemId}`).hide();
            }
            else if(response.item_quantity == response.max_quantity)
            {
                $(`#add-btn-${itemId}`).hide();
            }
            else
            {
                $(`#add-btn-${itemId}`).show();  
                $(`#remove-btn-${itemId}`).show(); 
            }
            
        },
        error: function(response){

        },
    });
}

