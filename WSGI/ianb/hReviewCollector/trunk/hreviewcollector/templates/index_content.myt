<p>
 <% c.total_urls %> URLs for a total size of 
 <% h.format_size(c.total_size) %>
</p>

<ul class="review-list">
% for hreview, page, size, embedded_size in c.review_parts:
 <li class="hreview-li">
  <% h.html(hreview) %>
  Size: <% h.format_size(size) %>
%   if embedded_size:
    + <% h.format_size(embedded_size) %> embedded
%   #end if
 </li>
% #end for
