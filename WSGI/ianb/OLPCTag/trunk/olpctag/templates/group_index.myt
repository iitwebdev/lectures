<h2>Select a Group</h2>

<blockquote>

<ul class="menu">
% for group in c.groups:
  <li><a href="<% group.slug | h %>"><% group.display_title | h %></a></li>
% #end for

</ul>

</blockquote>