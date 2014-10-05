//Autocomplete widget initialization, for custom name filler
$(document).bind('yourlabsWidgetReady', function() {
    $('body').on('initialize', '.autocomplete-light-widget[data-widget-bootstrap=fill-field-bootstrap]', function() {
        $(this).yourlabsWidget({
            namefield: $(this).closest('.row').find('.namefield input'),
            addToDeck:  function(choice, value) {
		var existing_choice = this.deck.find('[data-value="'+value+'"]');
		
		// Avoid duplicating choices in the deck.
		if (!existing_choice.length) {
		    var deckChoice = this.deckChoiceHtml(choice);
		    var fieldChoice = choice.clone();
		    this.namefield.val(fieldChoice.text())
		    // In case getValue() actually **created** the value, for example
		    // with a post request.
		    deckChoice.attr('data-value', value);
		    
		    this.deck.append(deckChoice);
		}
	    }
        })
    });
});

function fixHtml($elementsToFix) {
    $elementsToFix.find('.show-field').click(function() {
        var id = $(this).attr('id');
        $('div #' + id).removeClass('hide')
        $(this).parent().parent().addClass('hide')
        return false;
    });

    $elementsToFix.find('.delete-link').click(function() {
        var input_id = $(this).attr('id');
        $(this).parent().find('input#' + input_id).prop('checked', true);
        $elementsToFix.find('div#' + input_id).addClass('hide');
        return false;
    });

    $elementsToFix.find('.add_more').click(function() {
	var formsetName = $(this).attr('id')
        var form_idx = $('#id_' + formsetName + '-TOTAL_FORMS').val();
        var new_form = $('#empty_form').html().replace(/__prefix__/g, form_idx)
        $('.collection.' + formsetName).append(new_form);
        $('#id_' + formsetName + '-TOTAL_FORMS').val(parseInt(form_idx) + 1);
        fixHtml($('.collection.' + formsetName))
	return false;
    });
}


$(function () {
    fixHtml($(this));
})

$(function () {
    $('.date').datepicker();
    $('#id_date').datepicker();
})
