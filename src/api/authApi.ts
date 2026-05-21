import apiClient from "./axiosInstance";
import type { UserPublic } from "@/types/api";

const AUTH = '/auth'

export async function requestLogin(
    username: string,
    password: string,
): Promise<void> {
    const body = new URLSearchParams({ username, password })
    await apiClient.post(`${AUTH}/token`, body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
    })
}

export async function requestMe(): Promise<UserPublic> {
    const response = await apiClient.get<UserPublic>(`${AUTH}/me`)
    return response.data
}

export async function requestLogout(): Promise<void> {
    await apiClient.post(`${AUTH}/logout`)
}