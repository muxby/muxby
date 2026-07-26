import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "../api/client";
import { useAuthStore } from "../stores/authStore";

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: String(status),
    json: () => Promise.resolve(body),
  } as unknown as Response;
}

describe("api client", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    window.localStorage.clear();
    useAuthStore.setState({ token: null, user: null });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("login posts form-encoded credentials to /api/auth/login", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(200, { access_token: "jwt-1", token_type: "bearer" }),
    );

    const result = await api.login("doc@example.org", "secret123");

    expect(result.access_token).toBe("jwt-1");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/auth/login");
    expect(init.method).toBe("POST");
    const body = init.body as URLSearchParams;
    expect(body).toBeInstanceOf(URLSearchParams);
    expect(body.get("username")).toBe("doc@example.org");
    expect(body.get("password")).toBe("secret123");
  });

  it("sends the bearer token on authenticated requests", async () => {
    useAuthStore.setState({ token: "jwt-xyz" });
    fetchMock.mockResolvedValue(jsonResponse(200, []));

    await api.listHospitals();

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/hospitals");
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer jwt-xyz");
  });

  it("sets a JSON content type for JSON bodies", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(200, { id: 1, name: "General", region: "N", data_size: 5 }),
    );

    await api.createHospital({ name: "General", region: "N", data_size: 5 });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Headers;
    expect(headers.get("Content-Type")).toBe("application/json");
    expect(JSON.parse(init.body as string)).toEqual({
      name: "General",
      region: "N",
      data_size: 5,
    });
  });

  it("throws an ApiError carrying the backend detail message", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(400, { detail: "Email already registered" }),
    );

    const attempt = api.register({
      email: "dup@example.org",
      password: "secret123",
      full_name: "Dup",
    });

    await expect(attempt).rejects.toThrowError(ApiError);
    await expect(
      api.register({
        email: "dup@example.org",
        password: "secret123",
        full_name: "Dup",
      }),
    ).rejects.toThrow("Email already registered");
  });

  it("logs out when a request comes back 401 with a stored token", async () => {
    useAuthStore.setState({ token: "expired" });
    fetchMock.mockResolvedValue(
      jsonResponse(401, { detail: "Token expired" }),
    );

    await expect(api.listRounds()).rejects.toThrow("Token expired");
    expect(useAuthStore.getState().token).toBeNull();
  });

  it("resolves 204 responses without parsing a body", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 204,
      statusText: "No Content",
      json: () => Promise.reject(new Error("no body")),
    } as unknown as Response);

    await expect(api.deleteHospital(7)).resolves.toBeUndefined();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/hospitals/7");
    expect(init.method).toBe("DELETE");
  });
});
