function! s:is_null_or_empty(ret) abort
    let l:t = type(a:ret)
    if l:t==7
        return 1
    endif
    if l:t==3
        return len(a:ret)==0
    endif
    echom printf("%s",a:ret)
    return 0
endfunction

function! s:get_buffer_text() abort
    if &fileformat == 'unix'
        let line_ending = "\n"
    elseif &fileformat == 'dos'
        let line_ending = "\r\n"
    elseif &fileformat == 'mac'
        let line_ending = "\r"
    else
        echoerr "unknown value for the 'fileformat' setting: " . &fileformat
    endif
    return join(getline(1, '$'), line_ending).line_ending
endfunction

function! ws#lsp#documentOpen() abort
    let l:path = expand('%:p')
    let l:text = s:get_buffer_text()
    call ws#rpc#notify('notify_document_open', l:path, l:text)
endfunction

" goto definition {{{
function! s:goto(ret) abort
    if s:is_null_or_empty(a:ret)
        " no result
        return
    endif

    let l:pos = a:ret[0]
    " echom printf("goto %s", l:pos)
    call ws#position#goto(l:pos.uri, l:pos.range.start.line+1, l:pos.range.start.character+1)
endfunction

function! ws#lsp#gotoDefinition() abort
    let l:path = expand('%:p')
    let l:line = line('.')-1
    let l:col = col('.')-1
    call ws#rpc#request(function('s:goto'), 'request_document_definition', l:path, l:line, l:col)
endfunction
" }}}

" highlight {{{
function! s:highlight(ret) abort
    if s:is_null_or_empty(a:ret)
        " no result
        return
    endif
    "echo printf("highlight: %s", a:ret)
endfunction

function! ws#lsp#highlight() abort
    let l:path = expand('%:p')
    let l:line = line('.')-1
    let l:col = col('.')-1
    call ws#rpc#request(function('s:highlight'), 'request_document_highlight', l:path, l:line, l:col)
endfunction
" }}}

" did change {{{

function! ws#lsp#documentChange() abort
    echom "didChange"
    let l:path = expand('%:p')
    let l:text = s:get_buffer_text()
    call ws#rpc#notify('notify_document_change', l:path, l:text)
endfunction

" }}}

" omnifunc {{{
let s:context = {
            \   'id': 0,
            \ }

function! s:_complete(start, items) abort
    let l:completion = []

    for l:item in a:items
        call add(l:completion, l:item.insertText)
    endfor

    call complete(a:start, l:completion)
endfunction

function! s:complete(context, ret) abort
    if a:context.id != s:context.id
        return
    endif

    let l:t = type(a:ret)
    let l:start = s:context.start + 1
    if l:t==7
        return
    elseif l:t==3
        " list
        call s:_complete(l:start, a:ret)
    elseif l:t==4
        " dict
        call s:_complete(l:start, a:ret.items)
    endif
endfunction

function! ws#lsp#complete(findstart, base) abort
    if a:findstart
        let l:line = getline('.')
        let l:col = col('.')
        let l:start = l:col - 1
        while l:start > 0 && l:line[l:start - 1] =~ '\a'
            let l:start -= 1
        endwhile
        let s:context = {
                    \   'id' : s:context.id + 1,
                    \   'path' : expand('%:p'),
                    \   'line' : line('.')-1,
                    \   'col' : l:col,
                    \   'start': l:start,
                    \ }
        return s:context.col
    endif

    " sync current text
    call ws#lsp#documentChange()

    " send request
    call ws#rpc#request(function('s:complete', [s:context]),
                \ 'request_document_completion',
                \ s:context.path,
                \ s:context.line,
                \ s:context.col)

    return []
endfunction
" }}}