$('#addToWishList').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var product_id = button.data('product_id') // Extract info from data-* attributes
	var product_name = button.data('product_name')
	

    var modal = $(this)
    modal.find('.modal-title').text(product_name)

    // Create new wish list    
    $(document).on('submit', '#addNewWishListForm', function(e) {
        e.preventDefault()
        var name_input = $(this).find('input[name="name"]')
        var invalid_div = $(this).find('div.invalid-feedback')
        var valid_div = $(this).find('div.valid-feedback')
        var wish_lists_div = $("div #wishLists")
        var name = name_input.val() // Wish list name

        if (name.length > 3) {
			$.ajax({
				url: window.location.href,
				type: "POST",
				data: {
					"name": name,
					"csrfmiddlewaretoken": csrf_token,
					"action": "new_wish_list",
				},
				beforeSend: function(){
					valid_div.text("Creating new wish list");
					name_input.removeClass( "is-invalid" ).addClass( "is-valid" );
				},
				success: function(response){
					name_input.removeClass( "is-valid" )
					wish_lists_div.append(
					`<button name="list_id" value=${response.result} type="button" class="btn btn-warning m-2" data-toggle="modal" data-dismiss="modal">${name}</button>`
					);
				},
				error: function(error){
					console.log(error)
					invalid_div.text(error.responseJSON["result"]);
					name_input.removeClass( "is-valid" ).addClass( "is-invalid" );
				}                
			});
        } else {
          invalid_div.text("Whish list name must be > 3");
          name_input.removeClass( "is-valid" ).addClass( "is-invalid" );
        }
    });

	// Add product to wish list
    $(document).on('click', '.wish-list-button', function(e) {
        var wish_list_id = $( this ).val()

        $.ajax({
            url: window.location.href,
            type: "POST",
            data: {"wish_list_id": wish_list_id,
                   "product_id": product_id,
                   "csrfmiddlewaretoken": csrf_token,
                   "action": "add_prod_to_wl",
                  },
            success: function(response){
              modal.modal('hide');
            },
            error: function(error){
              alert(error.responseJSON["result"]);
            }                
        });

    });
});
