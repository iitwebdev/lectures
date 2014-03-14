% for bundle in c.bundles:
<% h.html(bundle) %>
% #end for

% if not c.bundles:
<div>
No bundles exist.  You must create one.
</div>
% #end if

<form action="<% c.url('') | h %>" method="POST">
<fieldset>
<legend>Create a bundle</legend>
<label for="title">Name:
<input type="text" name="title" id="title" width="70%">
</label><br>
<input type="submit" value="Create bundle">

</fieldset>
</form>


% if not c.bundles:
<script type="text/javascript">
document.getElementById('title').focus();
</script>
% #end if
