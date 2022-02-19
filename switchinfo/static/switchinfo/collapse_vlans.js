$(document).ready(function () {
    $('.show_tagged').click(function () {
        const interface_id = this.getAttribute('data-id')
        $('#tagged_' + interface_id).toggle()
    })
})
