let postComic = function () {
    let title = document.getElementById('title').value;
    let bodytext = document.getElementById('body').value;
    let tags = document.getElementById('tags').value;
    let image_list = getImageList();
    let page_turns = document.getElementById('pageturns');
    let preview_image = document.getElementById('preview_image');
    let post_button = document.getElementById('post-button');
    let preview_image_filename = '';
    let preview_image_src = preview_image.getAttribute('src');
    if (preview_image_src) {
        preview_image_filename = preview_image_src.replace(/^.*[\\\/]/, '');
    }
    let format = 'default';
    if (page_turns.checked) {
        format = 'page_turns'
    } else { format='infinite_canvas' }
    let post = {
        'title' : title,
        'body_text' : bodytext,
        'tags' : tags.split(','),
        'image_list' : image_list,
        'format' : format,
        'preview_image' : preview_image_filename
    };
    let post_json = JSON.stringify(post);
    if (!(post_button.getAttribute('data-id'))) {
        //We are in NEW POST mode
        fetch('/post_comic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: post_json,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Something went wrong');
            }
            return response.json();
        })
        .then(result => {
            let redirect = result['redirect'];
            window.location.replace(redirect);
            console.log('Post submitted successfully.')})
        .catch((error) => { alert('Post failed.');})
    } else {
        //We are in EDIT POST mode
        console.log('Submitting post edits');
        let comic_id = post_button.getAttribute('data-id');
        fetch('/modify_comic/'+comic_id.toString(), {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: post_json,
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('A problem!');
                }
                return response.json();
            })
            .then(result => {
                let redirect = result['redirect'];
                window.location.replace(redirect);
                console.log('Modification successful.')
            })
            .catch((error) => {console.log('Modification failed.')})
        ;
    }

};

let getImageList = function () {
    //console.log('Image list');
    let file_list = document.getElementById('file_list');
    let list_elements = file_list.querySelectorAll('li');
    let image_list = [];
    for (i=0; i<list_elements.length; i++) {
        let file_shortname = list_elements[i].querySelector('span.display_text').innerHTML;
        let file_path = list_elements[i].getAttribute('data-imgurl');
        let image_entry = {'file_shortname': file_shortname, 'file_path': file_path};
        image_list.push(image_entry)
    }
    return image_list
};