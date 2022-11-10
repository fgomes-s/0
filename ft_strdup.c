/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strdup.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/08 11:26:58 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/10 14:14:48 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strcpy(char *dest, char *src)
{
	int	i;

	i = 0;
	while (src[i] != '\0')
	{	
		dest[i] = src[i];
		i++;
	}
	dest[i] = '\0';
	return (dest);
}

char *ft_strdup(const char *s)
{
    char *ptr;

    ptr = (char *) malloc(ft_strlen(s) + 1);
    if (ptr != NULL)
    {
        strcpy(ptr, s);
    }
    return (ptr);
}



