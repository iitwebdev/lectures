<html>
<head>
<title>Tags</title>
</head>
<body>

% for tag in c.tags:

<h1><% tag.name %></h1>

%  if tag.description:
  <p class="tag-description">
    <% tag.description %>
  </p>
%  # end if

<div class="tag-pages">
%  for rating, page in tag.pages_by_rating(limit=1):

<a href="<% page.uri | h %>"
 target="_blank"><% page.display_title | h %></a>
%    if rating > 1:
    +<% rating %>
%    # end if
<a href="<% h.url_for(controller='info', uri=page.uri) %>">info</a><br>

%  # end for
</div>
    

% # end for

% if not c.tags:
  <p>No tags have been created</p>
% # end if

</body></html>
