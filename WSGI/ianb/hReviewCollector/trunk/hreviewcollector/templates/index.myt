<p>These are the reviews we found:
</p>


<ul class="review-list">
% for hreview in c.hreviews:

 <li class="hreview-li">
  <% h.html(hreview) %>
 </li>
% #end for
</ul>

% if not c.hreviews:
No reviews found!
% #end if
