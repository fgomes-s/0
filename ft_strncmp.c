/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strncmp.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/03 13:44:12 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/03 13:44:57 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"

int ft_strncmp(const char *s1, const char *s2, size_t n)
{
	size_t	i;
	unsigned char	a;
	unsigned char	b;

	i = 0;
	if (n != 0)
	{
		a = s1[i];
		b = s2[i];
	}
	while ((s1[i] != '\0') && (s1[i] == s2[i]) && (n > i + 1))
	{
		i++;
		a = s1[i];
		b = s2[i];
	}
	return (a - b);
}