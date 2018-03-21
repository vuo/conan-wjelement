#include <stdio.h>
#include <wjelement/wjelement.h>

int main()
{
	WJElement e = WJEFromString("{ \"foo\": true, \"bar\": -1 }");
	if (!e)
	{
		fprintf(stderr, "Error initializing WJElement.\n");
		return -1;
	}
	printf("Successfully initialized WJElement.  Output: %s\n", WJEToString(e, true));
	return 0;
}
