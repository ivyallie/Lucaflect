let comic_menu = document.getElementById('comic_menu');

        let listComicsByAuthor = function (id) {

            fetch('/getcomics/' + id, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
            })
                .then(response => response.json())
                .then(result => {
                    //console.log(result['comics']);
                    let comics = result['comics'];
                    generateMenu(comics);
                    console.log('Comics:', comics);
                })
                .catch(error => {
                    console.log('Error:', error);
                })

        }

        let generateMenu = function (comics) {
            let listing_template = document.getElementById('comic_menu_listing');
            comic_menu.innerHTML = '';
            for (c = 0; c < comics.length; c++) {
                let clone = listing_template.content.cloneNode(deep = true,);
                let name = clone.querySelector('span');
                let viewlink = clone.querySelector('a');
                name.innerHTML = comics[c]['title'];
                name.setAttribute('title', comics[c]['internal_title']);
                viewlink.setAttribute('href', '/comic/' + comics[c]['internal_title']);
                comic_menu.appendChild(clone)
            }


        }

        let postCollection = function () {
            let title = document.getElementById('title');
            let description = document.getElementById('description');
            let sequence = getComicSequence();
            console.log(sequence);
            let submit_button = document.getElementById('submit_button');
            let collection_id = null;
            if (submit_button.getAttribute('data-id')) {
                collection_id = submit_button.getAttribute('data-id')
            }

            let collection = {
                'title': title.value,
                'description': description.value,
                'sequence': sequence,
                'id':collection_id
            };

            let collection_json = JSON.stringify(collection);

            fetch('/collection/post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: collection_json,
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Something went wrong');
                    }
                    return response.json();
                })
                .then(result => {
                    //alert(result['redirect']);
                    let redirect = result['redirect'];
                    //console.log(redirect);
                    window.location.replace(redirect);
                })
                .catch((error) => {

                    alert(error);
                })

        };

        let getComicSequence = function () {
            //console.log('Image list');
            let collection_sequence = document.getElementById('collection_sequence');
            let list_elements = collection_sequence.querySelectorAll('li');
            let comic_sequence = [];
            for (i = 0; i < list_elements.length; i++) {
                let title_element = list_elements[i].querySelector('span');
                let internal_title = title_element.getAttribute('title');
                comic_sequence.push(internal_title);
            }
            return comic_sequence
        };

        let initialize_editor = function (sequence) {
        let sequence_editor = document.getElementById('collection_sequence');
        let listing_template = document.getElementById('comic_menu_listing');
        //console.log(sequence);
        //console.log(typeof(sequence))
        for (i=0;i<sequence.length;i++) {
            let clone = listing_template.content.cloneNode(deep = true,);
            let name = clone.querySelector('span');
            let viewlink = clone.querySelector('a');
            name.innerHTML = sequence[i]['title'];
            name.setAttribute('title', sequence[i]['internal_title']);
            viewlink.setAttribute('href', '/comic/' + sequence[i]['internal_title']);
            sequence_editor.appendChild(clone)
        }


    }