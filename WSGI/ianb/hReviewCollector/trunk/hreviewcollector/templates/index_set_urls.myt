<div>
 <form action="<% c.bundle_url('set_urls_submit') | h %>" method="POST">

  URL(s) to collect reviews from (enter one URL per line):<br>
  <textarea name="urls" rows=5 cols=60 style="width: 100%"><% c.url('examples/example1.html') | h %>
  </textarea>
  <br>
  <input type="submit" value="Save review URLs">

 </form>
</div>

