/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strnstr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/03 13:56:07 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/08 11:21:22 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strnstr(const char	*big, const char *little, size_t len)
{
	size_t	i;
	size_t	n;

	i = 0;
	n = 0;
	if (big == NULL && len == 0)
		return (NULL);
	if (little[i] == '\0')
		return ((char *) big);
	while (big[i] && i < len)
	{
		while (big[i + n] && (i + n) < len && big[i + n] == little[n])
			n++;
		if (little[n] == '\0')
			return ((char *)(big + i));
		i++;
		n = 0;
	}
	return (NULL);
}