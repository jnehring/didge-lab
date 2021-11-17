#include <stdio.h>

#include <math.h>

const long double p = 1.2929, n = 1.708e-5, c = 343.37;	// c = 331.45 * sqrt(293.16 / 273.16);

const long double PI = (long double) 3.14159265358979323846;

struct Seg{
  long double d0, d1, L;
  long double phi, a0, a01, a1, l, x1, x0, r0;
};

struct Seg *seg_new (long double L, long double d0, long double d1)
{
  struct Seg *seg = malloc (sizeof (struct Seg));

  seg->L = L;
  seg->d0 = d0;
  seg->d1 = d1;

  seg->a0 = PI * d0 * d0 / 4;
  seg->a01 = PI * (d0 + d1) * (d0 + d1) / 16;
  seg->a1 = PI * d1 * d1 / 4;
  seg->phi = atan ((d1 - d0) / (2 * L));

  seg->l = (d1 - d0) / (2 * sin (seg->phi));
  seg->x1 = d1 / (2 * sin (seg->phi));
  seg->x0 = seg->x1 - seg->l;
  seg->r0 = p * c / seg->a0;

  return seg;
}



long double complex **
ap (long double w, Eina_List * geo)
{
  Eina_List *ll;
  Seg *t_seg;
  long double L, d0, d1, a0, a01, a1, l, x0, x1, r0, rvw, kw;
  long double complex Tw, Zcw, ccoshlwl, csinhlwl, ccoshlwL, csinhlwL;
  long double complex x[2][2] = {{1, 0}, {0, 1}};
  long double complex y[2][2];
  long double complex **z;

  z = malloc (sizeof (long double complex *) * 2);
  z[0] = malloc (sizeof (long double complex) * 2);
  z[1] = malloc (sizeof (long double complex) * 2);

  EINA_LIST_FOREACH (geo, ll, t_seg)
  {
    L = t_seg->L;
    d0 = t_seg->d0;
    d1 = t_seg->d1;
    a0 = t_seg->a0;
    a01 = t_seg->a01;
    a1 = t_seg->a1;
    l = t_seg->l;
    x0 = t_seg->x0;
    x1 = t_seg->x1;
    r0 = t_seg->r0;
    
    rvw = sqrt (p * w * a01 / (n * PI));
    kw = w / c;
    Tw =kw * 1.045 / rvw + kw * (1.0 + 1.045 / rvw) * I;
    Zcw = r0 * (1.0 + 0.369 / rvw) - r0 * 0.369 / rvw * I;
    ccoshlwl = ccoshl (Tw * l);
    csinhlwl = csinhl (Tw * l);
    ccoshlwL = ccoshl (Tw * L);
    csinhlwL = csinhl (Tw * L);
    //printf ("%g %g %g %g %g\n", (double) w, (double) Tw, (double) Zcw), (double) ccoshlw, (double) csinhlw;

    if (d0 != d1)
      {
	y[0][0] = 
	  x1 / x0 * (ccoshlwl - csinhlwl / (Tw * x1));
	y[0][1] =
	  x0 / x1 * Zcw * csinhlwl;
	y[1][0] =
	  ((x1 / x0 - 1.0 / (Tw * Tw * x0 * x0)) * csinhlwl +
	   Tw * l / ((Tw * x0) * (Tw * x0)) * ccoshlwl) / Zcw;
	y[1][1] =
	  x0 / x1 * (ccoshlwl + csinhlwl / (Tw * x0));
      }
    else
      {
	y[0][0] =
	  ccoshlwL;
	y[0][1] =
	  Zcw * csinhlwL;
	y[1][0] =
	  csinhlwL / Zcw;
	y[1][1] =
	  ccoshlwL;
      }

    // dot product
    z[0][0] = x[0][0] * y[0][0] + x[0][1] * y[1][0];
    z[0][1] = x[0][0] * y[0][1] + x[0][1] * y[1][1];
    z[1][0] = x[1][0] * y[0][0] + x[1][1] * y[1][0];
    z[1][1] = x[1][0] * y[0][1] + x[1][1] * y[1][1];

    x[0][0] = z[0][0];
    x[0][1] = z[0][1];
    x[1][0] = z[1][0];
    x[1][1] = z[1][1];
  }

  return z;
}

long double complex
Za (long double w, Eina_List * geo)
{
  long double L, d1, a01, r0, rvw;
  long double complex Zcw;
  Seg *t_seg = eina_list_data_get (eina_list_last (geo));

  L = t_seg->L;
  d1 = t_seg->d1;
  a01 = t_seg->a01;
  r0 = t_seg->r0;
  
  rvw = sqrt (p * w * a01 / (n * PI));
  Zcw = r0 * (1.0 + 0.369 / rvw) - r0 * 0.369 / rvw * I;

  long double complex res = 0.5 * Zcw * (w * w * d1 * d1 / c / c + 0.6 * L * w * d1 / c * I);	//from geipel

  return res;
}

long double
cadsd_Ze (Eina_List * geo, double f)
{
  long double w = 2.0 * PI * (long double) f;
  long double complex a = Za (w, geo);

  long double complex **b = ap (w, geo);

  long double Ze =
    cabsl ((a * b[0][0] + b[0][1]) / (a * b[1][0] + b[1][1]));
  //printf ("Ze: %f\n", (double) Ze);
  free (b[0]);
  free (b[1]);
  free (b);
  return Ze;
}


int main() {

  double geo[3][2] = {{0,32}, {1500, 64}, {2000, 80}};
   // printf() displays the string inside quotation
   printf("Hello, World!");
   return 0;
}
