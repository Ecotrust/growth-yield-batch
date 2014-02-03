update stands_orig
set loccode = 606
where loccode = 708
and variant = 'WC';

update stands_orig
set loccode = 618
where loccode = 709
and variant = 'WC';

update stands_orig
set loccode = 615
where loccode = 710
and variant = 'WC';

update stands_orig
set loccode = 610
where loccode = 711
and variant = 'WC';

update stands_orig
set loccode = 612
WHERE variant = 'PN';


-- Set sitecls 0 to default of 2
update stands_orig
set sitecls = 2 
where sitecls = 0;