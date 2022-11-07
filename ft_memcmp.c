/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/03 14:23:49 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/03 14:24:31 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"

int	ft_memcmp(const void *str1, const void *str2, size_t n)
{
	size_t			i;
	char			*ptr1;
	char			*ptr2;
	unsigned char	c1;
	unsigned char	c2;

	i = 0;
	ptr1 = (char *) str1;
	ptr2 = (char *) str2;
	if (n == 0)
		return (0);
	while (i < (n - 1) && ptr1[i] == ptr2[i])
		i++;
	c1 = ptr1[i];
	c2 = ptr2[i];
	return (c1 - c2);
}