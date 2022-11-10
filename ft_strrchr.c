/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strrchr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/02 16:02:36 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/08 12:37:10 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strrchr(const char *s, int c)
{
	int		x;
	char	chr;
	char	*ptr;

	x = 0;
	chr = c;
	ptr = (void *)s;
	while (ptr[x] != '\0')
	{
		x++;
	}
	while (x >= 0)
	{
		if (ptr[x] == chr)
		{
			return (&ptr[x]);
		}
		x--;
	}
	return (NULL);
}