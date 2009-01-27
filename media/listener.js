$(document).ready(function(){
    $(".navi_tab").livequery('click',function(){
        $(".navi_tab").removeClass("tab_active").addClass("tab_inactive");
        $(this).removeClass("tab_inactive").addClass("tab_active");
        $("#main > div:visible").hide();

        var tab_id = $(this).attr("id");
        var tab_str = tab_id.substr(0,tab_id.length-4);
        $('#'+tab_str+'_body').show();
        ACTIVE_REGION = REGIONS.indexOf(tab_str);

        if (tab_str == "settings")
            $(".machine-control").hide();
        else
            $(".machine-control").show();
    });

    $(".order-machine-add-button").livequery('click', function(){
            var modvar = $(this).prev().val();
            var modname = $(this).prev().children("option:selected").html();
            var total_forms = $('#id_'+modvar+'-TOTAL_FORMS');
            var last_id = parseInt(total_forms.val()) - 1;
            var form = $("#"+modvar+"_set_item_"+last_id);

            total_forms.val(last_id+2);
            form.children(".region-choice-field").val(REGION_MAP[ACTIVE_REGION]);

            create_new_from_form(form, modvar, last_id);
            region_append(ACTIVE_REGION, form, modname, modvar);

            $(this).parent().parent().siblings(".empty-machine-msg").hide();
    });



    $(".item-delete").livequery('click',function(){
        popup_bg = '<div class="popup_bg"></div>';
        $("body").append(popup_bg);
        var item = $(this).parent().parent();
        jConfirm('Really delete item?', 'Confirm to delete item', function(r) {
            if (r==true) {
                set_item_field_value(item,"delete-field","checked");
                item.fadeOut(200);
                if (item.siblings(":visible").length == 0)
                    item.parent().siblings(".empty-machine-msg").show();
            }
            $(".popup_bg").remove();
        });
    });

    $(".cancel").livequery('click',function(){
        popup_bg = '<div class="popup_bg"></div>';
        $("body").append(popup_bg);
        jConfirm('Really change template? <br/>All content will be moved to main region.',
            'Change template', function(r) {
            if (r==true) {
                //$("#main").html(ORIGINAL);
                var items = $(".panel").children(".order-machine").children();
                move_item(0, items);
                $(".submit_form").click();
            } else {
                $(".popup_bg").remove();
            }
        });
    });

    $(".item-minimize").livequery('click',function(){
            var item = $(this).parent().next();
            if (item.is(":visible")) {
                $(this).html('<img src="'+IMG_ARROW_RIGHT_PATH+'" />');
                item.slideUp(200);
            } else {
                $(this).html('<img src="'+IMG_ARROW_DOWN_PATH+'" />');
                item.slideDown(200);
            }
    });

    $(".order-item").livequery('click',function(){
            $(".order-item").removeClass("active-item");
            $(this).addClass("active-item");
    });

    $(".submit_form").livequery('click',function(){
        zucht_und_ordnung();
        return true;
    });

    $(".order-machine-move-button").livequery('click', function(){
        var moveTo = $(this).prev().val();
        move_item(REGIONS.indexOf(moveTo),$(".active-item"));

        $("#"+moveTo+"_body").children(".empty-machine-msg").hide();
        if ($(this).parent().parent().siblings(".order-machine").children(":visible").length == 0)
            $(this).parent().parent().siblings(".empty-machine-msg").show();
    });

});
