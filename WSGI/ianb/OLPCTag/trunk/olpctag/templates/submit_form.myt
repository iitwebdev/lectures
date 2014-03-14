<html>
<head>
<title>Comment on <% c.page_title %></title>
</head>
<body>
<form action="<% h.url_for(controller='submit', action='submit') %>" method="POST">

<input type="hidden" name="from_js"
 value="<% request.params.get('from_js') | h %>">
<table style="width: 100%">

 <tr><td width="10%"><label for="uri">URL:</label></td>
     <td><input type="text" name="uri" id="uri" value="<% c.page_uri | h %>"
          style="width: 100%"></td>
 </tr>

 <tr><td><label for="title">Page Title:</label></td>
     <td><input type="text" name="title" id="title" value="<% c.page_title | h %>"
          style="width: 100%"></td>
 </tr>

 <tr><td><label for="tags">Tags:</label></td>
     <td><input type="text" name="tags" id="tags" value="<% c.default_tags | h %>"
          style="width: 100%"></td>
 </tr>

 <tr><td><label for="comments">Comments:</label></td>
     <td><textarea name="comments" id="comments" rows=3 style="width: 100%"><% c.comments | h %></textarea></td>
 </tr>

 <tr><td colspan=2 align=right>
       <input type="submit" value="submit">
       <button onclick="window.close(); return false">cancel</button>
     </td>
 </tr>

</table>

<script type="text/javascript">
  document.getElementById('tags').focus();
</script>

</body></html>
