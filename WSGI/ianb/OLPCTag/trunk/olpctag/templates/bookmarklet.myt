<p> 

You can tag items using this bookmarklet.  A bookmarklet is a piece of
Javascript you can drag into your bookmark toolbar; when you click on
the bookmark it will open a popup window for adding a tag.

</p>

<p>

Drag this link: <a href="javascript:void(open('<% h.url('submit') | h %>?from_js=t&amp;uri='+encodeURIComponent(location.href)+'&amp;title='+encodeURIComponent(document.title),'_blank','toolbar=no,width=700,height=250'))">post to <% c.group.display_title | h %></a>

</p>