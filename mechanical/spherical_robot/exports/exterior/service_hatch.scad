// Generated from config/dimensions.json. Do not edit.
$fn=160;
r=135.0; w=92.0; h=58.0; wall=4.0; shell_wall=2.8;
gap=0.3; lip=6.0;
seat_gap=0.25; border=7.0;
screws=[[-42.3, -25.3], [-42.3, 25.3], [42.3, -25.3], [42.3, 25.3]];
module slab(y,z) { translate([r/2,0,0]) cube([r,y,z],center=true); }
module patch(ro,ri,y,z) {
  intersection() { difference() { sphere(ro); sphere(ri); } slab(y,z); }
}
module bore(d,y,z) { translate([r-35,y,z]) rotate([0,90,0]) cylinder(h=45,d=d); }
module screws_cut(heads=false) {
  for(p=screws) {
    bore(3.4,p[0],p[1]);
    if(heads) translate([sqrt(r*r-pow(sqrt(p[0]*p[0]+p[1]*p[1])+6.4/2,2))-1.8,p[0],p[1]])
      rotate([0,90,0]) union() {
        cylinder(h=1.8-0.3,d1=3.4,d2=6.4);
        translate([0,0,1.8-0.3]) cylinder(h=10,d=6.4);
      }
  }
}
module hatch(av=false) {
  difference() {
    patch(r,r-wall,w,h);
    screws_cut(true);
    if(av) {
      bore(12.0,0,0);
      translate([r-2.0,0,0]) rotate([0,90,0])
        cylinder(h=10,d=18.0+2*gap);
      for(z=[-2.5,0,2.5]) bore(1.2,28.0,z);
    }
  }
}
module seat() {
  difference() {
    patch(r-shell_wall+0.4,r-wall-4.0,w+2*border,h+2*border);
    slab(w-2*lip,h-2*lip);
    intersection() {
      difference() { sphere(r+1); sphere(r-wall-seat_gap); }
      slab(w+2*gap,h+2*gap);
    }
    screws_cut(false);
  }
}
// Blank is the rolling configuration; AV is an alternative stationary-view lid.
if(part=="SERVICE_HATCH") hatch(false);
if(part=="SERVICE_HATCH_AV") hatch(true);
if(part=="SERVICE_HATCH_SEAT") seat();
