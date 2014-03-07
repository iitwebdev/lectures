/*
 * 7_setcookies.cpp
 * g++ -o 7_setcookies.cgi 7_setcookies.cpp -std=c++11
 */
#include <iostream>
using namespace std;

int main ()
{
 
   cout << "Set-Cookie:UserID=XYZ;\r\n";
   cout << "Set-Cookie:Password=XYZ123;\r\n";
   cout << "Set-Cookie:Domain=www.tutorialspoint.com;\r\n";
   cout << "Set-Cookie:Path=/perl;\n";
   cout << "Content-type:text/html\r\n\r\n";

   cout << "<html>\n";
   cout << "<head>\n";
   cout << "<title>Cookies in CGI</title>\n";
   cout << "</head>\n";
   cout << "<body>\n";

   cout << "Setting cookies" << endl;  
  
   cout << "<br/>\n";
   cout << "</body>\n";
   cout << "</html>\n";
   
   return 0;
}
