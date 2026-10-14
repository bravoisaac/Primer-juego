#include "Game/TenFeTrainingDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "TenFe.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

ATenFeTrainingDummy::ATenFeTrainingDummy()
{
    PrimaryActorTick.bCanEverTick = false;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    Mesh->SetCollisionProfileName(TEXT("Pawn"));
    Mesh->SetRelativeScale3D(FVector(0.7f, 0.7f, 1.8f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (CubeAsset.Succeeded())
    {
        Mesh->SetStaticMesh(CubeAsset.Object);
    }
}

float ATenFeTrainingDummy::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    const float Applied = FMath::Max(0.0f, DamageAmount);
    CurrentHealth = FMath::Max(0.0f, CurrentHealth - Applied);
    UE_LOG(LogTenFe, Display, TEXT("Muñeco de entrenamiento: %.0f / %.0f de vida"), CurrentHealth, MaxHealth);

    if (CurrentHealth <= 0.0f)
    {
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
        FTimerHandle RespawnHandle;
        GetWorldTimerManager().SetTimer(RespawnHandle, this, &ATenFeTrainingDummy::RestoreDummy, 2.0f, false);
    }
    return Applied;
}

void ATenFeTrainingDummy::RestoreDummy()
{
    CurrentHealth = MaxHealth;
    SetActorHiddenInGame(false);
    SetActorEnableCollision(true);
}
